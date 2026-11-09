"""Exercise deployment ordering and rollback with isolated fake Git/Docker commands."""

import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
REVISION = "a" * 40
BASH = "C:/Program Files/Git/bin/bash.exe" if os.name == "nt" else shutil.which("bash")


@pytest.fixture
def deployment(tmp_path):
    if not BASH or not Path(BASH).is_file():
        pytest.skip("Bash is required for deployment script checks")
    project = tmp_path / "app"
    scripts = project / "deploy/aws"
    scripts.mkdir(parents=True)
    runtime = project / ".runtime"
    runtime.mkdir()
    (project / ".env.aws").write_text("APP_ENV=production\n")
    for name in ("github-deploy-key", "github-known-hosts"):
        (runtime / name).write_text("test-only fixture\n")
    (runtime / "github-source.git").mkdir()
    script = project / "update.sh"
    # Relocate the fixed production root into the isolated fixture.
    script.write_text((ROOT / "deploy/aws/update-from-github.sh").read_text().replace("/opt/moveinmate", project.as_posix()), newline="\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "commands.log"
    archive_source = tmp_path / "source"
    for directory in ("src", "web", "tests", "alembic", "deploy/aws", "scripts"):
        (archive_source / directory).mkdir(parents=True, exist_ok=True)
    for relative in (
        "requirements.txt", "requirements-runtime.txt", "ruff.toml", "alembic.ini", ".dockerignore",
        "deploy/aws/Dockerfile", "scripts/migrate_database.py", "scripts/backup_database.py",
        "scripts/provision_auth_user.py", "scripts/import_database_settings.py", "scripts/crawl_data.py",
        "scripts/public_sources.json",
    ):
        shutil.copyfile(ROOT / relative, archive_source / relative)
    for relative in (".env", ".env.aws", ".runtime/private.json", "project-docs/private/report.json"):
        private_path = archive_source / relative
        private_path.parent.mkdir(parents=True, exist_ok=True)
        private_path.write_text("private-fixture-not-for-deployment\n")
    fake_commands = {
        "flock": '#!/usr/bin/env bash\ntest "${FAIL_AT:-}" != lock\n',
        "git": r'''#!/usr/bin/env bash
set -eu
case " $* " in
  *" remote get-url "*) printf '%s\n' 'https://github.com/congminh1705/MoveInMate-AI.git' ;;
  *" fetch "*) printf 'fetch %s\n' "$*" >> "$TEST_LOG" ;;
  *" rev-parse "*) printf '%s\n' "$TEST_REVISION" ;;
  *" archive "*)
    while test "$1" != --; do shift; done
    shift
    tar -cf - -C "$TEST_ARCHIVE_SOURCE" "$@" ;;
  *) exit 2 ;;
esac
''',
        "docker": r'''#!/usr/bin/env bash
set -eu
case "$1" in
 inspect)
   case "$*" in
     *org.opencontainers.image.revision*) printf '%s\n' "${TEST_CURRENT_REVISION:-old}" ;;
     *State.Health.Status*) printf '%s\n' healthy ;;
     *) printf '%s\n' sha256:old-image ;;
   esac ;;
 build)
   printf 'build %s\n' "$*" >> "$TEST_LOG"
   test -s "${@: -1}/requirements-runtime.txt"
   test "${FAIL_AT:-}" != build ;;
 run) printf 'validation %s\n' "$*" >> "$TEST_LOG"; test "${FAIL_AT:-}" != validation ;;
 tag) echo tag >> "$TEST_LOG" ;;
 *) exit 2 ;;
esac
''',
        "python3": '#!/usr/bin/env bash\nexec "' + Path(sys.executable).as_posix() + '" "$@"\n',
    }
    for name, content in fake_commands.items():
        path = bin_dir / name
        path.write_text(content, newline="\n")
        path.chmod(0o755)
    (scripts / "backup.sh").write_text(r'''#!/usr/bin/env bash
set -eu
echo backup >> "$TEST_LOG"
printf 'backup data' > backup.dump
sha256sum backup.dump > backup.dump.sha256
printf '%s/backup.dump\n' "$PWD"
''', newline="\n")
    (scripts / "compose.sh").write_text(r'''#!/usr/bin/env bash
set -eu
if test "$1" = run; then
  echo migration >> "$TEST_LOG"
  test "${FAIL_AT:-}" != migration
else
  printf 'up %s\n' "$MOVEINMATE_IMAGE" >> "$TEST_LOG"
  if test "${FAIL_AT:-}" = health && [[ "$MOVEINMATE_IMAGE" != *rollback* ]]; then exit 1; fi
fi
''', newline="\n")

    def run(*args, **env):
        bin_path = bin_dir.as_posix()
        if os.name == "nt":
            bin_path = "/" + bin_path[0].lower() + bin_path[2:]
        result = subprocess.run(
            [BASH, "-c", 'export PATH="$1:$PATH"; exec bash "$2" "${@:3}"', "--",
             bin_path, script.as_posix(), *args],
            input="test-ephemeral-token\n", text=True, capture_output=True,
            env={**os.environ, "TEST_LOG": log.as_posix(), "TEST_REVISION": REVISION,
                 "TEST_ARCHIVE_SOURCE": archive_source.as_posix(), **env}, timeout=30,
        )
        return result, log.read_text() if log.exists() else ""

    return run, runtime


def test_unchanged_revision_does_not_restart_or_backup(deployment):
    run, _ = deployment
    result, log = run("--deploy-key", "main", TEST_CURRENT_REVISION=REVISION)
    assert result.returncode == 0, result.stderr
    assert "fetch" in log
    assert "build" not in log and "backup" not in log and "up " not in log


@pytest.mark.parametrize("failure", ["build", "validation"])
def test_failed_candidate_does_not_touch_live_backend_or_database(deployment, failure):
    run, runtime = deployment
    result, log = run("--deploy-key", "main", FAIL_AT=failure)
    assert result.returncode != 0
    assert "backup" not in log and "migration" not in log and "up " not in log
    assert (runtime / "github-failed-revision").read_text().strip() == REVISION
    previous_log = log
    result, log = run("--deploy-key", "main")
    assert result.returncode == 0, result.stderr
    assert log.count("build") == previous_log.count("build")


def test_success_validates_then_backs_up_then_migrates_then_replaces(deployment):
    run, runtime = deployment
    result, log = run("--deploy-key", "main")
    assert result.returncode == 0, result.stderr
    assert log.index("validation") < log.index("backup") < log.index("migration") < log.index("up ")
    assert "git@github.com:congminh1705/MoveInMate-AI.git" in log
    assert json.loads((runtime / "github-deployment.json").read_text())["commit"] == REVISION
    assert not (runtime / "github-failed-revision").exists()


def test_candidate_archive_includes_runtime_dependencies_but_not_private_files(deployment):
    run, runtime = deployment
    result, _ = run("--deploy-key", "main")
    assert result.returncode == 0, result.stderr
    candidate = runtime / "github-builds" / REVISION
    assert (candidate / "requirements-runtime.txt").read_bytes() == (ROOT / "requirements-runtime.txt").read_bytes()
    assert (candidate / "requirements.txt").read_bytes() == (ROOT / "requirements.txt").read_bytes()
    for relative in (".env", ".env.aws", ".runtime/private.json", "project-docs/private/report.json"):
        assert not (candidate / relative).exists()


def test_python_validation_uses_separate_image_without_adding_tools_to_production(deployment):
    run, _ = deployment
    result, log = run("--deploy-key", "main")
    assert result.returncode == 0, result.stderr
    validation_image = f"moveinmate-aws:git-{REVISION[:12]}-validation"
    assert f"--target validation --tag {validation_image}" in log
    python_validation = next(line for line in log.splitlines() if line.startswith("validation ") and "pytest" in line)
    assert validation_image in python_validation
    assert "--network none --read-only" in python_validation
    assert f"up {validation_image}\n" not in log


def test_unhealthy_candidate_rolls_back_to_previous_image(deployment):
    run, runtime = deployment
    result, log = run("--deploy-key", "main", FAIL_AT="health")
    assert result.returncode != 0
    assert f"up moveinmate-aws:git-{REVISION[:12]}" in log
    assert "up moveinmate-aws:rollback-" in log
    assert (runtime / "github-failed-revision").read_text().strip() == REVISION
    assert not (runtime / "github-deployment.json").exists()


def test_failed_migration_leaves_previous_backend_running(deployment):
    run, _ = deployment
    result, log = run("--deploy-key", "main", FAIL_AT="migration")
    assert result.returncode != 0
    assert "backup" in log and "up " not in log


def test_auto_deployment_rejects_other_branches(deployment):
    run, _ = deployment
    result, log = run("--deploy-key", "vuong")
    assert result.returncode != 0 and not log


def test_overlapping_deployment_is_skipped(deployment):
    run, _ = deployment
    result, log = run("--deploy-key", "main", FAIL_AT="lock")
    assert result.returncode == 0 and not log


def test_manual_ephemeral_authentication_still_works(deployment):
    run, runtime = deployment
    result, log = run("main")
    assert result.returncode == 0, result.stderr
    assert "fetch" in log and "git@github.com" not in log
    assert json.loads((runtime / "github-deployment.json").read_text())["branch"] == "main"


@pytest.mark.parametrize("returncode,output", [(128, ""), (0, "")])
def test_enable_without_github_access_never_starts_timer(tmp_path, monkeypatch, capsys, returncode, output):
    from deploy.aws.configure_auto_deploy import REMOTE_OPERATOR

    (tmp_path / ".runtime").mkdir()
    (tmp_path / ".env.aws").touch()
    for name in ("github-deploy-key", "github-known-hosts"):
        (tmp_path / ".runtime" / name).touch()
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        assert command[:2] == ["git", "ls-remote"]
        return SimpleNamespace(returncode=returncode, stdout=output)

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(os, "geteuid", lambda: 0, raising=False)
    monkeypatch.setattr(sys, "argv", ["operator", "enable"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("{}"))
    operator = REMOTE_OPERATOR.replace('Path("/opt/moveinmate")', f"Path({str(tmp_path)!r})")
    with pytest.raises(SystemExit) as error:
        exec(compile(operator, "remote-operator", "exec"), {})
    assert error.value.code == 2
    assert len(calls) == 1
    assert json.loads(capsys.readouterr().out)["enabled"] is False

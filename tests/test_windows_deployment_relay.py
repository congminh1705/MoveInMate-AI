"""Verify commit selection, failure backoff and the single-instance relay lock."""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from deploy.aws import update_from_github, watch_github_main
from deploy.aws.watch_github_main import poll_once, single_instance

FIRST = "a" * 40
SECOND = "b" * 40
LOGGER = logging.getLogger("test-relay")


def test_new_main_commit_deploys_once_and_unchanged_commit_is_skipped(tmp_path):
    state = tmp_path / "state.json"
    calls = []

    def deploy():
        calls.append(True)
        return SimpleNamespace(returncode=0, stdout="already healthy")

    assert poll_once(state, lambda: FIRST, deploy, LOGGER)["status"] == "deployed"
    assert poll_once(state, lambda: FIRST, deploy, LOGGER)["status"] == "up_to_date"
    assert calls == [True]


def test_failed_commit_waits_until_any_contributor_pushes_a_new_commit(tmp_path):
    state = tmp_path / "state.json"
    calls = []

    def deploy():
        calls.append(True)
        return SimpleNamespace(returncode=1 if len(calls) == 1 else 0, stdout="")

    assert poll_once(state, lambda: FIRST, deploy, LOGGER)["status"] == "deployment_failed"
    assert poll_once(state, lambda: FIRST, deploy, LOGGER)["status"] == "waiting_for_new_commit"
    result = poll_once(state, lambda: SECOND, deploy, LOGGER)
    assert result["last_deployed"] == SECOND and "blocked_revision" not in result
    assert len(calls) == 2


def test_explicit_retry_can_redeploy_failed_commit(tmp_path):
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"blocked_revision": FIRST}))
    result = poll_once(state, lambda: FIRST, lambda: SimpleNamespace(returncode=0, stdout=""), LOGGER, retry=True)
    assert result["last_deployed"] == FIRST


def test_ssh_failure_retries_same_commit_after_backoff_without_logging_secrets(tmp_path, monkeypatch, caplog):
    state = tmp_path / "state.json"
    instant = "2026-10-11T07:00:00+00:00"
    monkeypatch.setattr(watch_github_main, "now", lambda: instant)
    calls = []

    def deploy():
        calls.append(True)
        if len(calls) == 1:
            raise watch_github_main.DeploymentConnectionError("private-token-must-not-appear")
        return SimpleNamespace(returncode=0, stdout="already healthy")

    result = poll_once(state, lambda: FIRST, deploy, LOGGER)
    assert result["status"] == "deployment_retry_scheduled" and "blocked_revision" not in result
    assert result["retry_after"] == "2026-10-11T07:00:30+00:00"
    assert poll_once(state, lambda: FIRST, deploy, LOGGER)["status"] == "waiting_for_retry"
    assert len(calls) == 1
    instant = result["retry_after"]
    result = poll_once(state, lambda: FIRST, deploy, LOGGER)
    assert result["last_deployed"] == FIRST and "retry_after" not in result
    assert len(calls) == 2
    assert "private-token-must-not-appear" not in caplog.text + state.read_text()


def test_connection_backoff_is_capped_and_new_commit_does_not_wait(tmp_path, monkeypatch):
    state = tmp_path / "state.json"
    instant = datetime.fromisoformat("2026-10-11T07:00:00+00:00")
    monkeypatch.setattr(watch_github_main, "now", lambda: instant.isoformat())

    def fail():
        raise watch_github_main.DeploymentConnectionError("SSH unavailable")

    for expected_delay in (30, 60, 120, 240, 300, 300):
        result = poll_once(state, lambda: FIRST, fail, LOGGER)
        retry_after = datetime.fromisoformat(result["retry_after"])
        assert retry_after - instant == timedelta(seconds=expected_delay)
        instant = retry_after
    result = poll_once(state, lambda: SECOND, fail, LOGGER)
    assert result["retry_revision"] == SECOND and result["connection_retry_count"] == 1
    result = poll_once(state, lambda: SECOND, lambda: SimpleNamespace(returncode=1, stdout=""), LOGGER, retry=True)
    assert result["status"] == "deployment_failed" and "retry_revision" not in result
    assert poll_once(state, lambda: SECOND, fail, LOGGER)["status"] == "waiting_for_new_commit"


@pytest.mark.parametrize("returncode,stderr", [
    (255, "ssh: connect to host: Connection timed out"),
    (1, "ssh: connect to host: Connection timed out\nCalledProcessError: Command '['ssh', '-o', 'BatchMode=yes']' returned non-zero exit status 255."),
])
def test_updater_classifies_ssh_errors_as_retryable(tmp_path, monkeypatch, returncode, stderr):
    monkeypatch.setattr(watch_github_main.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(
        returncode=returncode, stdout="", stderr=stderr,
    ))
    with pytest.raises(watch_github_main.DeploymentConnectionError):
        watch_github_main.run_updater(tmp_path, "test-host", tmp_path / "key", tmp_path / "known-hosts")


def test_relay_checks_main_every_fifteen_seconds():
    assert watch_github_main.POLL_INTERVAL_SECONDS == 15


@pytest.mark.parametrize("message", ["Permission denied (publickey)", "REMOTE HOST IDENTIFICATION HAS CHANGED"])
def test_ssh_authentication_and_host_key_errors_are_not_automatically_retried(tmp_path, monkeypatch, message):
    monkeypatch.setattr(watch_github_main.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(
        returncode=255, stdout="", stderr=message,
    ))
    result = watch_github_main.run_updater(tmp_path, "test-host", tmp_path / "key", tmp_path / "known-hosts")
    assert result.returncode == 255


def test_network_error_preserves_successful_revision_and_does_not_log_secret(tmp_path, caplog):
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"last_deployed": FIRST}))

    def fetch():
        raise ValueError("token-must-never-appear")

    def deploy():
        raise AssertionError("Must not deploy without reading main")

    result = poll_once(state, fetch, deploy, LOGGER)
    assert result["status"] == "source_unavailable" and result["last_deployed"] == FIRST
    assert "token-must-never-appear" not in caplog.text and "token-must-never-appear" not in state.read_text()


def test_server_lock_skip_is_not_recorded_as_a_successful_deployment(tmp_path):
    state = tmp_path / "state.json"
    result = poll_once(state, lambda: FIRST, lambda: SimpleNamespace(
        returncode=0, stdout="Another deployment is running; skipping this check."), LOGGER)
    assert result["status"] == "deployment_busy" and "last_deployed" not in result


def test_only_one_relay_can_hold_the_lock_and_it_is_released_after_exit(tmp_path):
    lock = tmp_path / "relay.lock"
    with single_instance(lock) as first:
        assert first
        with single_instance(lock) as second:
            assert not second
    with single_instance(lock) as third:
        assert third


@pytest.mark.skipif(os.name != "nt", reason="Windows console regression")
def test_updater_has_no_console_and_still_captures_output_and_failure(tmp_path, monkeypatch):
    run = subprocess.run

    def probe(command, **options):
        # Replace the deployment command with a real, harmless Windows child.
        script = (
            "import ctypes,json,sys; "
            "print(json.dumps({'console':ctypes.windll.kernel32.GetConsoleWindow(),"
            "'stdin':sys.stdin.read()})); "
            "print('updater failure',file=sys.stderr); sys.exit(7)"
        )
        return run([sys.executable, "-c", script], **options)

    monkeypatch.setattr(watch_github_main.subprocess, "run", probe)
    result = watch_github_main.run_updater(tmp_path, "test-host", tmp_path / "key", tmp_path / "known-hosts")
    assert json.loads(result.stdout) == {"console": 0, "stdin": ""}
    assert result.stderr.strip() == "updater failure"
    assert result.returncode == 7


@pytest.mark.skipif(os.name != "nt", reason="Windows console regression")
def test_credential_check_has_no_console_and_keeps_noninteractive_auth(tmp_path, monkeypatch):
    run = subprocess.run

    def probe(command, **options):
        assert command == ["git", "credential", "fill"]
        script = (
            "import ctypes,os,sys; "
            "assert ctypes.windll.kernel32.GetConsoleWindow()==0; "
            "assert os.environ['GIT_TERMINAL_PROMPT']=='0'; "
            "assert os.environ['GCM_INTERACTIVE']=='never'; "
            "assert 'host=github.com' in sys.stdin.read(); "
            "print('password=fixture-only-token')"
        )
        return run([sys.executable, "-c", script], **options)

    monkeypatch.setattr(update_from_github.subprocess, "run", probe)
    assert update_from_github.github_credential(tmp_path) == "fixture-only-token"


@pytest.mark.skipif(os.name != "nt", reason="Windows console regression")
@pytest.mark.parametrize("returncode", [0, 7])
def test_ssh_children_have_no_console_and_keep_redaction_and_exit_status(
    tmp_path, monkeypatch, capsys, returncode,
):
    key, known_hosts = tmp_path / "key", tmp_path / "known-hosts"
    key.touch()
    known_hosts.touch()
    run, popen = subprocess.run, subprocess.Popen
    token = "fixture-only-token"

    def probe_install(command, **options):
        assert command[0] == "ssh" and "sudo install" in command[-1]
        script = (
            "import ctypes,sys; "
            "assert ctypes.windll.kernel32.GetConsoleWindow()==0; "
            "assert sys.stdin.buffer.read()"
        )
        # run() calls Popen internally; bypass only the SSH substitution below.
        return run([sys.executable, "-c", script], **options)

    def probe_ssh(command, **options):
        if command[0] != "ssh":
            return popen(command, **options)
        assert "sudo bash" in command[-1]
        script = (
            "import ctypes,sys; "
            "assert ctypes.windll.kernel32.GetConsoleWindow()==0; "
            "token=sys.stdin.readline().strip(); "
            "print('received '+token); "
            f"sys.exit({returncode})"
        )
        return popen([sys.executable, "-c", script], **options)

    monkeypatch.setattr(update_from_github, "github_credential", lambda root: token)
    monkeypatch.setattr(update_from_github.subprocess, "run", probe_install)
    monkeypatch.setattr(update_from_github.subprocess, "Popen", probe_ssh)
    monkeypatch.setattr(sys, "argv", ["updater", "--host", "ubuntu@example.test", "--key", str(key), "--known-hosts", str(known_hosts)])
    if returncode:
        with pytest.raises(SystemExit) as error:
            update_from_github.main()
        assert error.value.code == returncode
    else:
        update_from_github.main()
    output = capsys.readouterr().out
    assert "received [redacted]" in output and token not in output

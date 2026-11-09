"""Watch GitHub main from a signed-in Windows session and deploy via SSH."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
POLL_INTERVAL_SECONDS = 15


class DeploymentConnectionError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(UTC).isoformat()


def fetch_revision(root: Path) -> str:
    from deploy.aws.update_from_github import REPOSITORY, github_credential

    with httpx.Client(timeout=30, headers={
        "Authorization": "Bearer " + github_credential(root),
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }) as client:
        response = client.get(f"https://api.github.com/repos/{REPOSITORY}/git/ref/heads/main")
        response.raise_for_status()
        revision = response.json()["object"]["sha"]
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Invalid main revision")
    return revision


def run_updater(root: Path, host: str, key: Path, known_hosts: Path) -> subprocess.CompletedProcess:
    from deploy.aws.update_from_github import hidden_process_options

    # pythonw has no standard streams. Capture the console interpreter's output
    # and suppress its console; redirecting output alone still creates a window.
    interpreter = str(root / ".venv/Scripts/python.exe") if os.name == "nt" else sys.executable
    result = subprocess.run([
        interpreter, str(root / "deploy/aws/update_from_github.py"), "--branch", "main",
        "--host", host, "--key", str(key.resolve()), "--known-hosts", str(known_hosts.resolve()),
    ], cwd=root, stdin=subprocess.DEVNULL, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=2400, **hidden_process_options())
    ssh_failed = result.returncode == 255 or (
        result.returncode and "'ssh'," in result.stderr and "returned non-zero exit status 255" in result.stderr
    )
    if ssh_failed and re.search(
        r"Connection (?:timed out|refused|reset)|No route to host|Could not resolve hostname",
        result.stdout + result.stderr,
        re.IGNORECASE,
    ):
        raise DeploymentConnectionError("SSH connection unavailable")
    return result


def read_state(path: Path) -> dict:
    if path.is_file():
        state = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise ValueError("Invalid relay state")
        return state
    return {}


def write_state(path: Path, state: dict) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def clear_connection_retry(state: dict) -> None:
    for key in ("retry_revision", "connection_retry_count", "retry_after"):
        state.pop(key, None)


def poll_once(state_path: Path, fetch, deploy, logger: logging.Logger, *, retry: bool = False) -> dict:
    state = read_state(state_path)
    state.update(pid=os.getpid(), checked_at=now())
    state.pop("stopped_at", None)
    try:
        revision = fetch()
    except Exception as error:
        # Exception messages and HTTP headers can contain credentials; log only the type.
        state.update(status="source_unavailable", error_type=type(error).__name__)
        write_state(state_path, state)
        logger.warning("GitHub check failed (%s); will retry next check.", type(error).__name__)
        return state
    state.update(last_seen=revision)
    state.pop("error_type", None)
    if state.get("retry_revision") not in {None, revision}:
        clear_connection_retry(state)
    if state.get("last_deployed") == revision:
        state["status"] = "up_to_date"
        clear_connection_retry(state)
    elif state.get("retry_revision") == revision and not retry and (
        datetime.fromisoformat(now()) < datetime.fromisoformat(state["retry_after"])
    ):
        state["status"] = "waiting_for_retry"
    elif state.get("blocked_revision") == revision and not retry:
        state["status"] = "waiting_for_new_commit"
    else:
        state.update(status="deploying", attempted_revision=revision, attempted_at=now())
        write_state(state_path, state)
        logger.info("Deploying main %s (pushes from every contributor are included).", revision)
        try:
            result = deploy()
            if result.returncode:
                raise RuntimeError("Deployment process failed")
        except DeploymentConnectionError as error:
            attempts = state.get("connection_retry_count", 0) + 1
            delay = min(30 * 2 ** min(attempts - 1, 4), 300)
            state.update(
                status="deployment_retry_scheduled", retry_revision=revision, connection_retry_count=attempts,
                retry_after=(datetime.fromisoformat(now()) + timedelta(seconds=delay)).isoformat(),
                error_type=type(error).__name__,
            )
            state.pop("blocked_revision", None)
            logger.warning("SSH unavailable; retrying main %s after %s seconds.", revision, delay)
        except Exception as error:
            clear_connection_retry(state)
            state.update(status="deployment_failed", blocked_revision=revision, error_type=type(error).__name__)
            logger.error("Deployment failed (%s); waiting for a new main commit or --retry.", type(error).__name__)
        else:
            # A deployment already holding the server lock was skipped, so recheck later.
            if "Another deployment is running; skipping this check." in result.stdout:
                state["status"] = "deployment_busy"
            else:
                state.update(status="deployed", last_deployed=revision, deployed_at=now())
                state.pop("blocked_revision", None)
                clear_connection_retry(state)
                logger.info("main %s is deployed or was already healthy.", revision)
    write_state(state_path, state)
    return state


@contextmanager
def single_instance(path: Path):
    with path.open("a+b") as stream:
        if path.stat().st_size == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, OSError):
            yield False
            return
        try:
            yield True
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--loop", action="store_true")
    mode.add_argument("--check", action="store_true", help="Check read access without deploying or starting a watcher")
    parser.add_argument("--retry", action="store_true", help="Retry a failed commit for this one-shot check")
    parser.add_argument("--host", required=True)
    parser.add_argument("--key", type=Path, default=ROOT / ".runtime/aws-deployment/deploy-key.pem")
    parser.add_argument("--known-hosts", type=Path, default=ROOT / ".runtime/aws-deployment/known_hosts")
    args = parser.parse_args()
    if args.loop and args.retry:
        parser.error("--retry is only supported for a one-shot check")
    if args.host.startswith("-"):
        parser.error("Invalid SSH host")
    for path in (args.key, args.known_hosts):
        if not path.is_file():
            parser.error(f"Missing SSH file: {path}")
    if args.check:
        print(json.dumps({"github_main": fetch_revision(ROOT), "read_access": True}))
        return
    runtime = ROOT / ".runtime/auto-deploy"
    runtime.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("moveinmate-relay")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(runtime / "windows-relay.log", maxBytes=1_048_576, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    state_path = runtime / "windows-relay.json"
    enabled_file = runtime / "windows-relay.enabled"
    with single_instance(runtime / "windows-relay.lock") as acquired:
        if not acquired:
            logger.info("Another relay instance is active; skipping.")
            return

        def deploy():
            result = run_updater(ROOT, args.host, args.key, args.known_hosts)
            # The updater redacts the ephemeral token before emitting any output.
            logger.info("Updater output:\n%s\n%s", result.stdout, result.stderr)
            return result

        while not args.loop or enabled_file.is_file():
            state = poll_once(state_path, lambda: fetch_revision(ROOT), deploy, logger, retry=args.retry)
            if not args.loop:
                print(json.dumps(state))
                if state["status"] in {
                    "source_unavailable", "deployment_failed", "waiting_for_new_commit",
                    "deployment_retry_scheduled", "waiting_for_retry",
                }:
                    raise SystemExit(1)
                return
            # Disabling the relay stops future checks; an active deployment finishes first.
            deadline = time.monotonic() + POLL_INTERVAL_SECONDS
            while enabled_file.is_file() and time.monotonic() < deadline:
                time.sleep(1)
        state = read_state(state_path)
        state.update(status="stopped", stopped_at=now())
        write_state(state_path, state)
        logger.info("Relay disabled; stopping.")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()

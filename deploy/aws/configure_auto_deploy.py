"""Prepare or enable EC2 polling with a repository-specific read-only deploy key."""

from __future__ import annotations

import argparse
import base64
import json
import shlex
import subprocess
from pathlib import Path

import httpx

REMOTE_OPERATOR = r'''
import base64, json, os, subprocess, sys
from pathlib import Path

root = Path("/opt/moveinmate")
runtime = root / ".runtime"
key = runtime / "github-deploy-key"
known_hosts = runtime / "github-known-hosts"
action = sys.argv[1]
payload = json.load(sys.stdin)
assert os.geteuid() == 0
assert (root / ".env.aws").is_file()

def write(path, content, mode):
    temporary = path.with_name(path.name + ".autodeploy.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)

def systemctl_value(*args):
    return subprocess.run(["systemctl", *args], capture_output=True, text=True).stdout.strip()

if action == "prepare":
    runtime.mkdir(exist_ok=True)
    if not key.exists():
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "moveinmate-main-autodeploy", "-f", str(key)], check=True)
    os.chmod(key, 0o600)
    os.chown(key, 0, 0)
    public_key = " ".join(subprocess.check_output(["ssh-keygen", "-y", "-f", str(key)], text=True).split()[:2])
    write(key.with_suffix(".pub"), (public_key + " moveinmate-main-autodeploy\n").encode(), 0o644)
    keys = payload["github_host_keys"]
    assert keys and all(isinstance(item, str) and "\n" not in item and "\r" not in item and item.startswith(("ssh-", "ecdsa-")) for item in keys)
    write(known_hosts, ("\n".join("github.com " + item for item in keys) + "\n").encode(), 0o644)
    allowed = {
        "update-from-github.sh": (root / "deploy/aws/update-from-github.sh", 0o750),
        "moveinmate-autodeploy.service": (Path("/etc/systemd/system/moveinmate-autodeploy.service"), 0o644),
        "moveinmate-autodeploy.timer": (Path("/etc/systemd/system/moveinmate-autodeploy.timer"), 0o644),
    }
    assert set(payload["files"]) == set(allowed)
    for name, (path, mode) in allowed.items():
        write(path, base64.b64decode(payload["files"][name], validate=True), mode)
    subprocess.run(["systemd-analyze", "verify", "/etc/systemd/system/moveinmate-autodeploy.service", "/etc/systemd/system/moveinmate-autodeploy.timer"], check=True)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    print(json.dumps({"prepared": True, "public_key": public_key + " moveinmate-main-autodeploy", "timer_enabled": systemctl_value("is-enabled", "moveinmate-autodeploy.timer")}))
elif action == "enable":
    assert key.is_file() and known_hosts.is_file()
    environment = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_SSH_COMMAND": "ssh -F /dev/null -i " + str(key) + " -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=" + str(known_hosts) + " -o ConnectTimeout=20"}
    result = subprocess.run(["git", "ls-remote", "git@github.com:congminh1705/MoveInMate-AI.git", "refs/heads/main"], env=environment, capture_output=True, text=True, timeout=40)
    if result.returncode or not result.stdout.strip():
        print(json.dumps({"enabled": False, "reason": "GitHub has not authorized this deploy key for the private repository; timer left unchanged."}))
        raise SystemExit(2)
    subprocess.run(["systemctl", "enable", "--now", "moveinmate-autodeploy.timer"], check=True)
    subprocess.run(["systemctl", "start", "--no-block", "moveinmate-autodeploy.service"], check=True)
    print(json.dumps({"enabled": True, "github_main": result.stdout.split()[0]}))
elif action == "status":
    state = {
        "timer_enabled": systemctl_value("is-enabled", "moveinmate-autodeploy.timer"),
        "timer_active": systemctl_value("is-active", "moveinmate-autodeploy.timer"),
        "service": systemctl_value("show", "moveinmate-autodeploy.service", "--property=ActiveState,SubState,Result,ExecMainStatus"),
    }
    deployment = runtime / "github-deployment.json"
    if deployment.is_file():
        state["deployment"] = json.loads(deployment.read_text())
    failed = runtime / "github-failed-revision"
    if failed.is_file():
        state["failed_revision"] = failed.read_text().strip()
    print(json.dumps(state))
'''


def prepare_payload(directory: Path) -> dict:
    response = httpx.get("https://api.github.com/meta", timeout=30)
    response.raise_for_status()
    return {
        "github_host_keys": response.json()["ssh_keys"],
        "files": {
            name: base64.b64encode((directory / name).read_bytes().replace(b"\r\n", b"\n")).decode("ascii")
            for name in ("update-from-github.sh", "moveinmate-autodeploy.service", "moveinmate-autodeploy.timer")
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "enable", "status"))
    parser.add_argument("--host", required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--known-hosts", type=Path, required=True)
    args = parser.parse_args()
    if args.host.startswith("-"):
        parser.error("Invalid SSH host")
    for path in (args.key, args.known_hosts):
        if not path.is_file():
            parser.error(f"Missing SSH file: {path}")
    payload = prepare_payload(Path(__file__).parent) if args.action == "prepare" else {}
    ssh = [
        "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=20",
        "-o", f"UserKnownHostsFile={args.known_hosts.resolve()}", "-i", str(args.key.resolve()), args.host,
        "sudo python3 -c " + shlex.quote(REMOTE_OPERATOR) + " " + args.action,
    ]
    result = subprocess.run(ssh, input=json.dumps(payload).encode(), capture_output=True, timeout=90)
    output = result.stdout.decode("utf-8", errors="replace")
    print(output, end="")
    if result.stderr:
        print(result.stderr.decode("utf-8", errors="replace"), end="")
    if result.returncode:
        raise SystemExit(result.returncode)
    if args.action == "prepare":
        state = json.loads(output.splitlines()[-1])
        private_dir = Path(__file__).resolve().parents[2] / ".runtime/auto-deploy"
        private_dir.mkdir(parents=True, exist_ok=True)
        (private_dir / "github-deploy-key.pub").write_text(state["public_key"] + "\n", encoding="utf-8")
        (private_dir / "prepared.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

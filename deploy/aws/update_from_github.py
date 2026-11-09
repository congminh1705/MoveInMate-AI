"""Fetch and deploy GitHub code on EC2 using credentials sent over SSH stdin."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
from pathlib import Path

REPOSITORY = "congminh1705/MoveInMate-AI"


def hidden_process_options() -> dict:
    """Keep console tools windowless when launched by the Windows relay."""
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def github_credential(project_root: Path) -> str:
    result = subprocess.run(
        ["git", "credential", "fill"],
        cwd=project_root,
        input=f"protocol=https\nhost=github.com\npath={REPOSITORY}.git\n\n",
        text=True,
        capture_output=True,
        timeout=30,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"},
        **hidden_process_options(),
    )
    values = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    token = values.get("password", "")
    if result.returncode or not token or "\n" in token or "\r" in token:
        raise RuntimeError("GitHub authentication is unavailable; sign in to Git on this computer first.")
    return token


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--known-hosts", type=Path, required=True)
    parser.add_argument("--branch", default="main")
    args = parser.parse_args()
    if args.host.startswith("-"):
        parser.error("Invalid SSH host")
    for path in (args.key, args.known_hosts):
        if not path.is_file():
            parser.error(f"Missing SSH file: {path}")
    root = Path(__file__).resolve().parents[2]
    token = github_credential(root)
    ssh = [
        "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
        "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=3",
        "-o", f"UserKnownHostsFile={args.known_hosts.resolve()}",
        "-i", str(args.key.resolve()), args.host,
    ]
    script_path = "/opt/moveinmate/deploy/aws/update-from-github.sh"
    # Only this small operator script is bootstrapped locally. Application code
    # is fetched by EC2 directly from GitHub and pinned to the fetched commit.
    script = Path(__file__).with_name("update-from-github.sh").read_bytes().replace(b"\r\n", b"\n")
    subprocess.run(
        [*ssh, f"sudo install -m 0750 /dev/stdin {script_path}"],
        input=script, check=True, timeout=45,
        **hidden_process_options(),
    )
    with subprocess.Popen(
        [*ssh, f"sudo bash {script_path} {shlex.quote(args.branch)}"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        **hidden_process_options(),
    ) as process:
        assert process.stdin is not None and process.stdout is not None
        process.stdin.write((token + "\n").encode("utf-8"))
        process.stdin.close()
        for raw_line in process.stdout:
            line = raw_line.decode("utf-8", errors="replace")
            print(line.replace(token, "[redacted]"), end="", flush=True)
        result = process.wait()
    if result:
        raise SystemExit(result)


if __name__ == "__main__":
    main()

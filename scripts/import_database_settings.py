import argparse
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def private_write(path: Path, content: str) -> None:
    descriptor = os.open(str(path) + ".tmp", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        output.write(content)
    os.chmod(str(path) + ".tmp", 0o600)
    os.replace(str(path) + ".tmp", path)


def migrate_settings(env_file: Path, expected_database: str, reset_code: str = "") -> dict:
    from src.config import Settings
    from src.repositories.settings import DATABASE_FIELDS, SettingsStore
    from src.repositories.store import Store
    from src.services.login_reset import capture_baseline

    env_file = env_file.resolve(strict=True)
    if env_file.name != ".env.aws":
        raise ValueError("cloud_env_file_required_local_env_preserved")
    original = env_file.read_text(encoding="utf-8")
    configuration = dotenv_values(env_file)
    settings = Settings(_env_file=env_file, settings_source="env")
    database_url = make_url(settings.require_database_url())
    if database_url.database != expected_database or expected_database != "moveinmate_prod":
        raise ValueError("cloud_database_target_mismatch")
    backup_dir = env_file.parent / ".runtime" / "settings-backups"
    backup_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    backup = backup_dir / f"bootstrap-{datetime.now(UTC):%Y%m%dT%H%M%S%f}.env"
    private_write(backup, original)
    key = settings.settings_encryption_key or Fernet.generate_key().decode()
    if not settings.settings_encryption_key:
        private_write(env_file, original.rstrip() + f"\nSETTINGS_ENCRYPTION_KEY={key}\n")
    store = Store(settings.require_database_url())
    try:
        repository = SettingsStore(store, key)
        if configuration.get("SETTINGS_SOURCE") == "postgresql":
            settings = repository.load(settings)
        if reset_code:
            settings = settings.model_copy(update={"login_reset_code": reset_code})
            capture_baseline(store, settings.local_auth_site_id)
        count = repository.save(settings)
        loaded = repository.load(settings)
        if any(getattr(loaded, name) != getattr(settings, name) for name in DATABASE_FIELDS):
            raise ValueError("settings_roundtrip_failed")
        keep_lines = []
        removed_names = {name.upper() for name in DATABASE_FIELDS} | {"SETTINGS_SOURCE", "SETTINGS_ENCRYPTION_KEY", "LOGIN_RESET_ENABLED"}
        for line in original.splitlines():
            variable = line.split("=", 1)[0].strip().removeprefix("export ")
            if variable not in removed_names:
                keep_lines.append(line)
        keep_lines.extend(("SETTINGS_SOURCE=postgresql", f"SETTINGS_ENCRYPTION_KEY={key}",
                           f"LOGIN_RESET_ENABLED={'true' if reset_code or settings.login_reset_enabled else 'false'}"))
        private_write(env_file, "\n".join(keep_lines) + "\n")
        return {"settings": count, "encrypted": True, "backup": str(backup), "local_credentials_preserved": True}
    finally:
        store.engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="Move cloud configuration to encrypted PostgreSQL rows.")
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--expected-database", required=True)
    parser.add_argument("--reset-code-stdin", action="store_true")
    arguments = parser.parse_args()
    reset_code = sys.stdin.readline().strip() if arguments.reset_code_stdin else ""
    if arguments.reset_code_stdin and not 4 <= len(reset_code) <= 128:
        parser.error("Reset code must be between 4 and 128 characters")
    import json

    print(json.dumps(migrate_settings(arguments.env_file, arguments.expected_database, reset_code)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

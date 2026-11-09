"""Provision a configured local identity into the MoveInMate membership table."""

from __future__ import annotations

import argparse

from src.config import get_settings
from src.repositories import Store


def main() -> None:
    parser = argparse.ArgumentParser(description="Map a configured local identity to a role and scope.")
    parser.add_argument("--subject", required=True, help="Local account subject, e.g. local:admin.")
    parser.add_argument("--role", choices=("resident", "manager"), required=True)
    parser.add_argument("--site-id", required=True)
    parser.add_argument("--resident-id", help="Required for resident; omit for manager.")
    args = parser.parse_args()

    settings = get_settings()
    store = Store(
        settings.require_database_url(),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout_seconds,
        connect_timeout=settings.db_connect_timeout_seconds,
    )
    try:
        store.initialize()
        result = store.provision_membership(
            auth_subject=args.subject,
            role=args.role,
            site_id=args.site_id,
            resident_id=args.resident_id,
        )
        print(
            f"Provisioned role={result['role']} site={result['site_id']} "
            f"resident={result['resident_id'] or '-'}"
        )
    finally:
        store.engine.dispose()


if __name__ == "__main__":
    main()

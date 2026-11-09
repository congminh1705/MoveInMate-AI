#!/usr/bin/env bash
set -eu
umask 077

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../.." && pwd)"
backup_dir="$project_root/.runtime/aws-backups"
timestamp="$(date -u +%Y%m%dT%H%M%S)-$$"
container_path="/tmp/moveinmate-$timestamp.dump"
backup_path="$backup_dir/moveinmate-$timestamp.dump"
mkdir -p "$backup_dir"

cleanup() {
    bash "$script_dir/compose.sh" exec -T db rm -f "$container_path" >/dev/null 2>&1 || true
}
trap cleanup EXIT

bash "$script_dir/compose.sh" exec -T db sh -eu -c 'umask 077; pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl --file="$1"' sh "$container_path"
bash "$script_dir/compose.sh" exec -T db pg_restore --list "$container_path" >/dev/null
bash "$script_dir/compose.sh" cp "db:$container_path" "$backup_path"
chmod 600 "$backup_path"
cd "$backup_dir"
sha256sum "$(basename -- "$backup_path")" > "$backup_path.sha256"
printf '%s\n' "$backup_path"

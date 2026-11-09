#!/usr/bin/env bash
set -eu

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$project_root"
exec docker compose --env-file "$project_root/.env.aws" -f "$project_root/deploy/aws/docker-compose.aws.yml" "$@"

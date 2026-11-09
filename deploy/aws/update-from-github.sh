#!/usr/bin/env bash
set -euo pipefail
umask 077
trap 'printf "GitHub updater preflight failed at line %s.\n" "$LINENO" >&2' ERR

auth_mode=stdin
if test "${1:-}" = --deploy-key; then
    auth_mode=deploy-key
    shift
fi
unset GIT_TRACE GIT_TRACE_CURL GIT_CURL_VERBOSE
branch="${1:-main}"
project_root="${2:-/opt/moveinmate}"
repository="https://github.com/congminh1705/MoveInMate-AI.git"
[[ "$branch" =~ ^[a-zA-Z0-9][a-zA-Z0-9/_-]*$ ]] || exit 2
test "$project_root" = /opt/moveinmate
cd "$project_root"
if test "$auth_mode" = stdin; then
    # Manual authentication is ephemeral and never saved on the server.
    IFS= read -r github_token
    github_token="${github_token%$'\r'}"
    test -n "$github_token"
else
    test "$branch" = main
    test -s .runtime/github-deploy-key
    test -s .runtime/github-known-hosts
    export GIT_SSH_COMMAND="ssh -F /dev/null -i $project_root/.runtime/github-deploy-key -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$project_root/.runtime/github-known-hosts -o ConnectTimeout=20"
fi
test -f .env.aws
test -f deploy/aws/compose.sh
mkdir -p .runtime/github-builds
command -v flock >/dev/null
exec 9>.runtime/github-update.lock
flock -n 9 || { echo 'Another deployment is running; skipping this check.'; exit 0; }

source_repo="$project_root/.runtime/github-source.git"
if ! test -d "$source_repo"; then
    git init --bare "$source_repo" >/dev/null
    git --git-dir="$source_repo" remote add origin "$repository"
fi
test "$(git --git-dir="$source_repo" remote get-url origin)" = "$repository"
if test "$auth_mode" = stdin; then
    github_header="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$github_token" | base64 -w0)"
    GIT_TERMINAL_PROMPT=0 GIT_CONFIG_COUNT=1 \
    GIT_CONFIG_KEY_0=http.https://github.com/.extraheader \
    GIT_CONFIG_VALUE_0="$github_header" \
        git --git-dir="$source_repo" fetch --no-tags --depth=1 origin \
        "+refs/heads/$branch:refs/remotes/origin/$branch"
    unset github_token github_header
else
    GIT_TERMINAL_PROMPT=0 git --git-dir="$source_repo" fetch --no-tags --depth=1 \
        git@github.com:congminh1705/MoveInMate-AI.git \
        "+refs/heads/main:refs/remotes/origin/main"
fi
revision="$(git --git-dir="$source_repo" rev-parse "refs/remotes/origin/$branch^{commit}")"
image="moveinmate-aws:git-${revision:0:12}"
current_revision="$(docker inspect moveinmate-aws-backend-1 \
    --format '{{index .Config.Labels "org.opencontainers.image.revision"}}' 2>/dev/null || true)"
current_health="$(docker inspect moveinmate-aws-backend-1 \
    --format '{{.State.Health.Status}}' 2>/dev/null || true)"
if test "$current_revision" = "$revision" && test "$current_health" = healthy; then
    printf 'Already running GitHub %s at %s; no restart needed.\n' "$branch" "$revision"
    exit 0
fi
failed_revision="$project_root/.runtime/github-failed-revision"
if test "$auth_mode" = deploy-key && test -f "$failed_revision" && test "$(cat "$failed_revision")" = "$revision"; then
    printf 'GitHub %s previously failed validation/deployment; waiting for a new commit.\n' "$revision"
    exit 0
fi
mark_failed() { printf '%s\n' "$revision" > "$failed_revision"; }
trap mark_failed ERR

if grep -Eq '^SETTINGS_SOURCE=postgresql\s*$' .env.aws; then
    for required_path in src/repositories/settings.py alembic/versions/20261010_0007_settings_reset.py; do
        if ! git --git-dir="$source_repo" cat-file -e "$revision:$required_path"; then
            echo 'Refusing an application version without encrypted database settings support.' >&2
            mark_failed
            exit 1
        fi
    done
fi

build_dir="$project_root/.runtime/github-builds/$revision"
mkdir -p "$build_dir"
git --git-dir="$source_repo" archive "$revision" -- \
    src web tests alembic deploy/aws requirements.txt requirements-runtime.txt ruff.toml alembic.ini .dockerignore \
    scripts/migrate_database.py scripts/backup_database.py scripts/provision_auth_user.py \
    scripts/import_database_settings.py scripts/crawl_data.py scripts/public_sources.json \
    | tar -x -C "$build_dir"
printf 'Building GitHub %s at %s.\n' "$branch" "$revision"
docker build --label "org.opencontainers.image.revision=$revision" \
    --label "org.opencontainers.image.source=$repository" \
    --tag "$image" --file "$build_dir/deploy/aws/Dockerfile" "$build_dir"
validation_image="$image-validation"
docker build --target validation --tag "$validation_image" \
    --file "$build_dir/deploy/aws/Dockerfile" "$build_dir"

# Validate without production credentials, network or database mounts.
docker run --rm --network none --read-only --tmpfs /tmp:rw,exec,size=256m \
    --env APP_ENV=test --env LLM_PROVIDER=auto --env PYTHON_DOTENV_DISABLED=1 \
    --volume "$build_dir:/app:ro" \
    --entrypoint /bin/bash "$validation_image" -ec \
    'python -m ruff check --no-cache src alembic && python -m pytest --noconftest -p no:cacheprovider -q --tb=short tests/test_local_auth_core.py tests/test_authorization_core.py tests/test_conversation_policy.py tests/test_aws_deployment.py tests/test_windows_deployment_relay.py'
docker run --rm --network none --read-only --workdir /workspace \
    --volume "$build_dir:/workspace:ro" node:22-alpine /bin/sh -ec \
    'node --check web/app.js && node --check web/portal.js && node --check web/login-reset.js && node --test tests/web/*.test.mjs'

previous_image="$(docker inspect moveinmate-aws-backend-1 --format '{{.Image}}')"
rollback_image="moveinmate-aws:rollback-$(date -u +%Y%m%dT%H%M%S)"
docker tag "$previous_image" "$rollback_image"
backup_path="$(bash deploy/aws/backup.sh | tail -n1)"
test -s "$backup_path"
(cd "$(dirname -- "$backup_path")" && sha256sum -c "$(basename -- "$backup_path").sha256")
export MOVEINMATE_IMAGE="$image"
bash deploy/aws/compose.sh run --rm --no-deps -T backend python -m alembic upgrade head
if ! bash deploy/aws/compose.sh up -d --no-build --no-deps --wait --wait-timeout 180 backend; then
    echo 'New backend failed health checks; restoring previous application image.' >&2
    MOVEINMATE_IMAGE="$rollback_image" bash deploy/aws/compose.sh \
        up -d --no-build --no-deps --wait --wait-timeout 180 backend
    echo "Deployment failed. Database backup retained at $backup_path; no automatic schema downgrade." >&2
    mark_failed
    exit 1
fi
docker tag "$image" moveinmate-aws:latest
rm -f -- "$failed_revision"
trap - ERR
python3 - "$repository" "$branch" "$revision" "$image" "$previous_image" "$rollback_image" "$backup_path" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

repository, branch, revision, image, previous, rollback, backup = sys.argv[1:]
state = {
    "source": "github",
    "repository": repository,
    "branch": branch,
    "commit": revision,
    "image": image,
    "previous_image": previous,
    "rollback_image": rollback,
    "database_backup": backup,
    "deployed_at": datetime.now(timezone.utc).isoformat(),
}
path = Path(".runtime/github-deployment.json")
temporary = path.with_suffix(".tmp")
temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
temporary.replace(path)
print(json.dumps(state))
PY

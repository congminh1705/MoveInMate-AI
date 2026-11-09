# MoveInMate AI

A resident onboarding assistant with checklists, resident profiles, management requests, ticket history and role-scoped AI tools. FastAPI serves the API and HTML/CSS/JavaScript frontend; PostgreSQL stores application data; LangGraph orchestrates the assistant.

This repository is a source release for self-hosting. It does not include operational accounts, resident records, API keys, databases or access to the original deployment.

## Features

- Local login, resident/management roles, first-login setup and password recovery.
- Household profiles, onboarding checklists, resident-card and vehicle workflows.
- Management tickets, notifications, decisions and status history.
- LangGraph tools scoped to the authenticated user.
- BM25/phrase retrieval with source and residential-site filtering.
- Optional LLM, speech-to-text and text-to-speech integrations.

## Run with Docker

Install Docker and Docker Compose v2. On Windows, use Docker Desktop with Linux containers. Python 3.11+ can generate the configuration secrets below.

```powershell
git clone https://github.com/congminh1705/MoveInMate-AI.git
Set-Location MoveInMate-AI
Copy-Item .env.example .env
```

Edit `.env` before starting:

| Variable | Configuration |
|---|---|
| `POSTGRES_DB` | `moveinmate_dev` for a new development database |
| `POSTGRES_TEST_DB` | `moveinmate_test`; must differ from the application DB |
| `POSTGRES_PASSWORD` | A new database password |
| `DATABASE_URL` | Host Python URL with matching user/password/DB and `localhost` host |
| `TEST_DATABASE_URL` | Separate test database URL |
| `AUTH_JWT_SECRET` | A new random secret of at least 32 characters |
| `SETTINGS_ENCRYPTION_KEY` | A new Fernet key, backed up separately from the database |
| `LOCAL_AUTH_ADMIN_PASSWORD` | Your own management account password |
| `LOCAL_AUTH_USER_PASSWORD` | Your own configured resident account password |

Generate a fresh URL-safe password/JWT secret for each purpose:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Generate a Fernet key using only the Python standard library:

```powershell
python -c "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

Use URL-safe database credentials to avoid URL escaping issues. Compose sets the database host to `db` inside the backend container. Keep `AUTH_MODE=required`, `ALLOW_DEMO_AUTH=false`, `SHOW_LOCAL_LOGIN_CREDENTIALS=false` and `LOGIN_RESET_ENABLED=false`. Tracing is disabled by default. Configure your own LLM provider/API key for AI features; speech providers need their own configuration.

```powershell
docker compose config --quiet
docker compose build backend
docker compose up -d --wait db
docker compose run --rm --no-deps backend python -m scripts.migrate_database
```

Only for a new, disposable demo database, optionally seed synthetic records:

```powershell
docker compose run --rm --no-deps backend python -m scripts.seed_demo
```

Then start the application:

```powershell
docker compose up -d --wait --wait-timeout 180 backend
Invoke-RestMethod http://localhost:8000/api/v1/health
```

Open **http://localhost:8000** and sign in with the `LOCAL_AUTH_*` credentials you configured. API documentation is at **http://localhost:8000/docs**. There is no operational password distributed with this repository.

Public source URLs are listed in `scripts/public_sources.json`. To import them, run `docker compose exec -T backend python scripts/crawl_data.py` and restart the backend. Bundled knowledge examples are demo material, not approved building regulations.

## Develop on the host

Start PostgreSQL and configure host URLs in `.env`, then run:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m scripts.migrate_database
.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Do not re-seed an existing database with data you need to keep. Back up important databases and verify restoration before migration.

## Structure and validation

- `src/`: API, agent, authorization, services and repositories.
- `web/`: static frontend and assets; no frontend build step.
- `alembic/`: database migrations.
- `scripts/`: migration, backup, catalog import, crawling and demo seeding.
- `tests/`: Python and JavaScript tests.
- `eval/fixtures/`: explicitly synthetic evaluation fixtures.
- `deploy/aws/`: deployment templates to adapt to your own infrastructure.

Python tests require a separate PostgreSQL test database. Tests can delete/recreate test data. Never point `TEST_DATABASE_URL` at an operational database.

```powershell
.venv\Scripts\python.exe -m ruff check src tests alembic scripts/seed_demo.py deploy/aws/*.py
.venv\Scripts\python.exe -m pytest tests/ -q --tb=short
node --test tests/web/*.test.mjs
```

CI is available as a manual workflow in the **Actions** tab. This copy does not install prompt-collection hooks from the original development environment.

See [architecture](docs/architecture.md), [public release notes](docs/PUBLIC_RELEASE.md), [security](SECURITY.md) and [contributing](CONTRIBUTING.md).

Historical design documents, the presentation and demo video are available in [project-docs](project-docs/README.md). Some historical references point to evidence not included in this source release. Use the setup instructions above for this repository.

## License and attribution

The original source is distributed under the [MIT License](LICENSE), copyright 2026 AI20K Build Phase. The copyright notice is retained; this copy does not claim sole authorship for the personal repository owner.

Bundled Open Mascot code retains its author's [MIT license](web/vendor/open-mascot/LICENSE). Publishing source does not transfer the original deployment's accounts, data or infrastructure access.

# Public release notes

This repository is an independent source snapshot with a new Git history. The original MIT license, copyright notice and bundled third-party license are retained.

## Included

- Application source, static frontend assets and the login password layout fix.
- Database migrations, synthetic evaluation fixtures, applicable tests and runtime/development dependencies.
- Docker Compose and deployment templates adapted for this repository. SSH deployment commands require an explicit server target.
- The `project-docs/` source folder, excluding `de_tai.png`, added after the initial release. Operational addresses in Markdown were replaced with examples and four student identifiers were redacted from the presentation PDF. Contributor names are retained. The presentation deck and demo video are included.

## Excluded

- Original commit history, branches, tags, issues, pull requests and private contributor email history.
- `.env`, local runtime files, databases, backups, cloud keys and developer profiles.
- AI prompt logs, prompt-collection hooks, cohort ingestion scripts and their dedicated tests.
- Historical operational evidence outside the reviewed `project-docs/` folder.
- Original organization CODEOWNERS and internal workflow configuration.

Operational host addresses and old repository deployment targets have been removed or replaced. Public provider endpoints, government source URLs, public residential-site catalog sources and clearly synthetic test credentials remain where needed by the application and tests.

CI is manual only. Tracing is disabled in the example environment. LLM and speech providers require the new operator's own configuration.

This source release does not migrate live accounts, tickets, private settings, uploaded resident documents or running services. Configure your own environment and database as described in README.md.

Publication checks cover known-secret matching against the source environment, credential patterns, excluded paths, deployment targets and Git history. They do not certify production readiness or eliminate the need to review future changes.

## Validation on 2026-11-09

- Ruff: passed.
- Python: 1,201 tests passed using a disposable PostgreSQL container, separate from the operational database.
- JavaScript: 245 tests passed.
- Startup smoke check: homepage returned HTTP 200; health reported `configuration_required` because no LLM credentials were supplied.
- Gitleaks v8.30.1: no unreviewed findings. Four inline allowances document synthetic test secrets, an unsigned fake JWT and an idempotency key.
- Known-secret comparison: no matches against eight nonempty secret fields of at least eight characters in the source environment.
- Application Python source and both MIT license files were preserved. Changes concern publication packaging, documentation, deployment targets and synthetic-test annotations.

The production Docker image was not built as part of these publication checks.

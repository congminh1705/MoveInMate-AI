# Security

Do not post credentials, private documents, personal data or an unpatched exploit in a public issue. Contact the repository owner privately; use GitHub private vulnerability reporting if the owner has enabled it.

Keep secrets in environment variables or a suitable secret store. `.env.example` contains placeholders only. Use separate development and test databases. Tracing is opt-in and may transmit application content to the configured provider. LLM and speech features also send requests to their configured providers.

If a credential is exposed, revoke or rotate it first. Removing it in a later commit does not remove earlier copies. Then review repository history and affected services.

The public release excludes the original Git history, operational database, backups, machine credentials and prompt-collection hooks. The separately reviewed `project-docs/` material includes a demo video and presentation; student identifiers in the presentation PDF have been redacted. Automated scans reduce risk but cannot prove that every kind of sensitive information is absent.

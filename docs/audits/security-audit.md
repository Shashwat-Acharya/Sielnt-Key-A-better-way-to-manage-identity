# Security and Permissions Audit Report

## Critical

- None found after the environment and database cleanup.

## High

- Role-based access control is modeled in the database, but authorization enforcement in request handlers is still not implemented end-to-end.
- No automated secret scanning or pre-commit guardrails are present in the repository.
- File and directory permissions cannot be enforced by repository code alone; the project assumes the developer and deployment environment will protect `.env`, logs, and generated secrets.
- The PostgreSQL bootstrap path depends on a privileged `postgres` account; that credential was not available locally, so I could not complete an end-to-end permission bootstrap against the live server.

## Medium

- Audit logging must remain carefully sanitized because request and response payloads can easily leak sensitive identity data if raw objects are persisted.
- The QR and challenge flows are not yet implemented in the request layer, so the security properties described in the roadmap are still partly aspirational.
- The project currently depends on environment variables for secrets, which is correct, but that requires deployment discipline and clear operational documentation.

## Low

- The repository ignores common secret, log, and virtual environment artifacts correctly, but the `.env.example` file still needs to be kept current whenever a new secret is introduced.
- The admin site is enabled and populated, which is useful for development but should be hardened before any broader deployment.

## Suggestions

- Add least-privilege PostgreSQL roles for migrations, application runtime, and read-only audit access.
- Add request throttling and authentication middleware once the protocol endpoints exist.
- Add a secrets management strategy for production environments.
- Add a documented permissions checklist for local development, CI, and deployment hosts.
- Add a secure bootstrap workflow that only requires the superuser credential during initial provisioning, then operates with least-privilege roles afterward.

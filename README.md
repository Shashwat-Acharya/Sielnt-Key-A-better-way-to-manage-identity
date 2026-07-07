# Silent Key

Silent Key is a protocol-first identity platform that treats identity, not a single device, as the trust anchor. The repository currently focuses on the Django backend, PostgreSQL-backed persistence, QR-based pairing primitives, audit logging, and a research track for biometric cryptosystems.

## Motivation

The project explores portable identity without depending on one primary device or a password reset flow. The design keeps business rules in the backend, exposes thin clients, and separates research topics from the production protocol.

## Features

- Django-based identity backend
- PostgreSQL persistence with environment-driven configuration
- QR pairing and challenge-response protocol models
- Audit logging and permission-role models
- Standalone API database helper with explicit connection lifecycle management
- Research documentation for biometrics, threshold cryptography, WebAuthn, and post-quantum directions

## Current Status

- Django project initialized and wired to PostgreSQL
- Identity app, admin registration, and migrations are present
- QR generation uses Segno in the API layer
- The root URL now serves the canonical identity landing page for identity.silentkey.me
- Protocol-stage models now include device, pairing, challenge, session, and key-pair concepts
- Research documentation and audit reports are included in this repository update

## Architecture

The codebase follows a layered approach:

- `backend/` contains Django configuration, models, admin, and request handling
- `api/` contains standalone API/database helpers and QR generation utilities
- `core/` contains the C++ security-sensitive engine for future biometric and cryptographic work
- `infra/` contains PostgreSQL bootstrap and infrastructure helpers
- `research/` contains the research corpus and design notes

See [docs/README.md](docs/README.md) and [docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md) for deeper context.

## Repository Structure

- [backend/](backend/) - Django backend project and identity app
- [api/](api/) - Database helper and QR-related utilities
- [core/](core/) - C++ processing and cryptographic engine
- [infra/](infra/) - PostgreSQL bootstrap and environment setup
- [research/](research/) - Research notes, references, experiments, and benchmarks
- [tests/](tests/) - Validation and schema checks
- [docs/](docs/) - Architecture notes, design principles, and audit reports

## Technology Stack

- Python 3.14+
- Django 6
- PostgreSQL 18
- psycopg 3
- Segno for QR generation
- C++ for the future biometric/cryptographic core

## Installation

1. Install dependencies with Poetry.
2. Copy `.env.example` to `.env` and fill in the database and secret values.
3. Ensure PostgreSQL is available locally or remotely.
4. Run Django migrations from the `backend/` project.

Example:

```bash
poetry install
cp .env.example .env
python backend/manage.py migrate
```

## Development Setup

- Use a local PostgreSQL instance for development
- Set `USE_MIGRATION_USER=True` when applying migrations
- Keep `DEBUG=True` only for local development
- Use the backend Django app for protocol work and the `api/` package for standalone helpers

## Configuration

The project reads configuration from environment variables or `.env`.

Key settings:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DB_NAME`
- `AUDIT_DB_NAME`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `MIGRATION_DB_USER`
- `MIGRATION_DB_PASSWORD`
- `AUDIT_DB_USER`
- `AUDIT_DB_PASSWORD`
- `CANONICAL_HOST`
- `USE_MIGRATION_USER`
- `DB_CONN_MAX_AGE`
- `DB_CONNECT_TIMEOUT`

## Database Configuration

The backend uses PostgreSQL connections configured in `backend/config/settings.py`. Django persistent connections are enabled through `CONN_MAX_AGE`, and the standalone API helper now opens connections explicitly instead of at import time.

The repository does not hardcode database passwords in code. Use `.env` or your deployment environment to provide credentials.

## Environment Variables

See [`.env.example`](.env.example) for the full list of supported variables and defaults.

## Usage

Run the Django backend:

```bash
python backend/manage.py runserver
```

Apply migrations:

```bash
python backend/manage.py migrate
```

Run schema validation:

```bash
python tests/pg_schema_check.py
```

## Screenshots

Placeholder screenshots will be added as the UI and client surfaces are implemented.

- Login / QR pairing flow: pending
- Admin workflow: pending
- Research dashboard: pending

## Security Considerations

- Biometrics are treated as a research track, not as a direct cryptographic key source
- Secrets are loaded from the environment, not hardcoded in the repository
- QR payloads should remain short-lived and session-only
- Audit logging should avoid storing raw secrets or unfiltered request bodies

## Research Section

The [research/](research/) directory contains the long-term research track, reference material, experiment logs, benchmarks, and open questions that support the protocol design.

## Documentation

- [Design principles](docs/DESIGN_PRINCIPLES.md)
- [Documentation index](docs/README.md)
- [Backend notes](backend/README.md)
- [API notes](api/README.md)
- [Infrastructure notes](infra/README.md)
- [Research index](research/README.md)
- [Repository audit](docs/audits/repository-audit.md)
- [Database audit](docs/audits/database-audit.md)
- [Security audit](docs/audits/security-audit.md)

## Contribution Guide

- Keep changes small and documented
- Add tests for behavior changes when practical
- Keep biometric research separate from core protocol logic
- Update the relevant docs when a model, environment variable, or workflow changes

## Testing

- `python backend/manage.py test`
- `python tests/pg_schema_check.py`

## Roadmap

1. Complete the pairing and challenge-response protocol flows
2. Add secure key lifecycle management and recovery planning
3. Expand the desktop client and thin interfaces
4. Continue research into biometric cryptosystems and threshold schemes
5. Add CI, linting, and automated deployment checks

## License

See [LICENSE.md](LICENSE.md) and [Enterprise License Agreement (ELA).md](Enterprise%20License%20Agreement%20(ELA).md).

## Acknowledgements

- Django project scaffolding and documentation patterns
- PostgreSQL and psycopg for relational storage
- Segno for QR code generation
- The research literature on WebAuthn, fuzzy extractors, secure sketch, fuzzy vaults, and post-quantum cryptography

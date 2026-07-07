# Database Audit Report

## Critical

- None found in the current code after the refactor.

## High

- The repository does not yet use a dedicated connection pool library such as `psycopg_pool`. Django persistent connections are enabled through `CONN_MAX_AGE`, which is acceptable for the current scope, but true pool management is not yet in place.
- The audit database is declared in settings, but it is not yet isolated from the primary identity database at the model-routing level because the audit log model still references the primary user table.
- The repository now includes a bootstrap SQL file for roles, databases, and schema grants, but I could not execute it locally because the `postgres` superuser password was not available in this workspace.

## Medium

- Database credentials are now environment-driven, but the project still relies on local `.env` management for development and deployment.
- Backup and recovery automation are not documented or implemented in the repository.
- Transaction boundaries are not yet codified around higher-level identity workflows because the protocol handlers still need to be built.
- Schema initialization is present through migrations, but separate operational guidance for the primary and audit databases is still needed.

## Low

- The validation script still assumes a local PostgreSQL superuser for full schema checks.
- Some database names are still environment-configurable rather than fully discovery-based, which is normal for a repo at this stage but should be documented in deployment runbooks.

## Suggestions

- Add explicit transaction helpers for pairing and challenge workflows.
- Add backup and restore runbooks for both databases.
- Introduce database-specific health checks in CI.
- Evaluate whether the audit log should be denormalized or replicated if a full two-database split becomes necessary.
- Store the PostgreSQL superuser credential in the deployment secret manager so bootstrap and disaster recovery can be validated non-interactively.

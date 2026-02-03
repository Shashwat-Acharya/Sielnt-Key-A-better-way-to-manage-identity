/* ============================================================
   SilentKey PostgreSQL Bootstrap
   Purpose:
   - Create databases
   - Create roles
   - Apply least-privilege permissions
   - Prepare schemas for migrations
   ============================================================ */

-- ============================================================
-- 1. CREATE ROLES (NO SUPERUSER, NO CREATEDB)
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'sk_app_user') THEN
        CREATE ROLE sk_app_user NOINHERIT LOGIN PASSWORD 'REPLACE_APP_PASSWORD';
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'sk_migration_user') THEN
        CREATE ROLE sk_migration_user NOINHERIT LOGIN PASSWORD 'REPLACE_MIGRATION_PASSWORD';
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'sk_readonly_audit') THEN
        CREATE ROLE sk_readonly_audit NOINHERIT LOGIN PASSWORD 'REPLACE_READONLY_PASSWORD';
    END IF;
END $$;

-- ============================================================
-- 2. CREATE DATABASES (OWNED BY postgres, NOT APP USERS)
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'silentkey_identity') THEN
        CREATE DATABASE silentkey_identity;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'silentkey_audit') THEN
        CREATE DATABASE silentkey_audit;
    END IF;
END $$;

-- ============================================================
-- 3. LOCK DOWN DEFAULT PUBLIC ACCESS
-- ============================================================

REVOKE ALL ON DATABASE silentkey_identity FROM PUBLIC;
REVOKE ALL ON DATABASE silentkey_audit FROM PUBLIC;

-- ============================================================
-- 4. GRANT DATABASE CONNECT PERMISSIONS
-- ============================================================

GRANT CONNECT ON DATABASE silentkey_identity TO sk_app_user;
GRANT CONNECT ON DATABASE silentkey_identity TO sk_migration_user;

GRANT CONNECT ON DATABASE silentkey_audit TO sk_app_user;
GRANT CONNECT ON DATABASE silentkey_audit TO sk_migration_user;
GRANT CONNECT ON DATABASE silentkey_audit TO sk_readonly_audit;

-- ============================================================
-- 5. IDENTITY DATABASE SETUP
-- ============================================================

\c silentkey_identity

-- Create schema owned by migration user
CREATE SCHEMA IF NOT EXISTS identity AUTHORIZATION sk_migration_user;

-- Schema usage
GRANT USAGE ON SCHEMA identity TO sk_app_user;
GRANT USAGE ON SCHEMA identity TO sk_migration_user;

-- Default privileges for future tables
ALTER DEFAULT PRIVILEGES
FOR ROLE sk_migration_user
IN SCHEMA identity
GRANT SELECT, INSERT, UPDATE ON TABLES TO sk_app_user;

-- ============================================================
-- 6. AUDIT DATABASE SETUP
-- ============================================================

\c silentkey_audit

-- Create schema owned by migration user
CREATE SCHEMA IF NOT EXISTS audit AUTHORIZATION sk_migration_user;

-- Schema usage
GRANT USAGE ON SCHEMA audit TO sk_app_user;
GRANT USAGE ON SCHEMA audit TO sk_migration_user;
GRANT USAGE ON SCHEMA audit TO sk_readonly_audit;

-- App user: write-only
ALTER DEFAULT PRIVILEGES
FOR ROLE sk_migration_user
IN SCHEMA audit
GRANT INSERT ON TABLES TO sk_app_user;

-- Read-only audit role
ALTER DEFAULT PRIVILEGES
FOR ROLE sk_migration_user
IN SCHEMA audit
GRANT SELECT ON TABLES TO sk_readonly_audit;

-- ============================================================
-- 7. SAFETY HARDENING
-- ============================================================

-- Prevent accidental object creation by app user
REVOKE CREATE ON SCHEMA identity FROM sk_app_user;
REVOKE CREATE ON SCHEMA audit FROM sk_app_user;

-- Ensure migration user can create objects
GRANT CREATE ON SCHEMA identity TO sk_migration_user;
GRANT CREATE ON SCHEMA audit TO sk_migration_user;

-- ============================================================
-- END OF BOOTSTRAP
-- ============================================================
-- Note: Remember to replace placeholder passwords with secure values.
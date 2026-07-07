#!/usr/bin/env python3
"""
SilentKey PostgreSQL Schema Verification Test Suite
Tests database setup, roles, permissions, and security configuration
"""
import os
import sys
import psycopg
from typing import Dict, List, Tuple

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class PostgresSchemaValidator:
    """Validates PostgreSQL database schema and permissions"""

    def __init__(self):
        self.test_results: List[Tuple[str, bool, str]] = []
        self.passwords = {
            "sk_app_password": os.environ.get("sk_app_password") or os.environ.get("DB_PASSWORD"),
            "sk_migration_password": os.environ.get("sk_migration_password") or os.environ.get("MIGRATION_DB_PASSWORD"),
            "sk_readonly_password": os.environ.get("sk_readonly_password") or os.environ.get("AUDIT_DB_PASSWORD"),
            "PG_SUPER_PASS": os.environ.get("PG_SUPER_PASS"),
        }
        self.host = os.environ.get("DB_HOST", "localhost")
        self.identity_db = os.environ.get("DB_NAME", "silentkey_identity")
        self.audit_db = os.environ.get("AUDIT_DB_NAME", "silentkey_audit")

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
        print(f"{status} - {test_name}")
        if message:
            print(f"       {message}")
        self.test_results.append((test_name, passed, message))

    def get_postgres_connection(self):
        """Get connection to postgres database as superuser"""
        return psycopg.connect(
            dbname="postgres",
            user="postgres",
            password=self.passwords["PG_SUPER_PASS"],
            host=self.host,
            autocommit=True,
        )

    def get_user_connection(self, dbname: str, user: str, password: str):
        """Get connection as specific user"""
        return psycopg.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=self.host,
            autocommit=True,
        )

    def test_databases_exist(self, conn):
        """Test that required databases exist"""
        print(f"\n{BLUE}=== Testing Database Existence ==={RESET}")
        cur = conn.cursor()

        databases = [self.identity_db, self.audit_db]
        for db in databases:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db,))
            exists = cur.fetchone() is not None
            self.log_test(f"Database '{db}' exists", exists)

        cur.close()

    def test_roles_exist(self, conn):
        """Test that required roles exist"""
        print(f"\n{BLUE}=== Testing Roles Existence ==={RESET}")
        cur = conn.cursor()

        roles = [
            ("sk_app_user", "Application user role"),
            ("sk_migration_user", "Migration user role"),
            ("sk_readonly_user", "Read-only audit role"),
        ]

        for role, description in roles:
            cur.execute(
                """
                SELECT rolname, rolsuper, rolcreatedb, rolinherit, rolcanlogin
                FROM pg_roles WHERE rolname = %s
            """,
                (role,),
            )
            result = cur.fetchone()
            exists = result is not None
            self.log_test(f"Role '{role}' exists", exists, description)

            if exists:
                rolname, rolsuper, rolcreatedb, rolinherit, rolcanlogin = result
                # Verify security attributes
                self.log_test(
                    f"Role '{role}' is NOT superuser", not rolsuper, "Security check"
                )
                self.log_test(
                    f"Role '{role}' cannot create databases",
                    not rolcreatedb,
                    "Security check",
                )
                self.log_test(
                    f"Role '{role}' has NOINHERIT",
                    not rolinherit,
                    "Security check",
                )
                self.log_test(f"Role '{role}' can login", rolcanlogin)

        cur.close()

    def test_password_authentication(self):
        """Test that passwords work correctly for each role"""
        print(f"\n{BLUE}=== Testing Password Authentication ==={RESET}")

        # Test each user can authenticate with their password
        test_users = [
            ("sk_app_user", self.passwords["sk_app_password"], "silentkey_identity"),
            (
                "sk_migration_user",
                self.passwords["sk_migration_password"],
                "silentkey_identity",
            ),
            (
                "sk_readonly_user",
                self.passwords["sk_readonly_password"],
                "silentkey_audit",
            ),
        ]

        for user, password, dbname in test_users:
            try:
                conn = self.get_user_connection(dbname, user, password)
                conn.close()
                self.log_test(
                    f"User '{user}' can authenticate with password",
                    True,
                    f"Connected to {dbname}",
                )
            except Exception as e:
                self.log_test(
                    f"User '{user}' can authenticate with password",
                    False,
                    f"Error: {str(e)}",
                )

    def test_database_connect_permissions(self, conn):
        """Test that users have correct CONNECT permissions"""
        print(f"\n{BLUE}=== Testing Database CONNECT Permissions ==={RESET}")
        cur = conn.cursor()

        # Expected permissions: database -> list of users who should have CONNECT
        expected_permissions = {
            "silentkey_identity": ["sk_app_user", "sk_migration_user"],
            "silentkey_audit": [
                "sk_app_user",
                "sk_migration_user",
                "sk_readonly_user",
            ],
        }

        for db, expected_users in expected_permissions.items():
            cur.execute(
                """
                SELECT pg_catalog.has_database_privilege(%s, %s, 'CONNECT')
            """,
                ("sk_app_user", db),
            )
            for user in expected_users:
                cur.execute(
                    """
                    SELECT pg_catalog.has_database_privilege(%s, %s, 'CONNECT')
                """,
                    (user, db),
                )
                has_connect = cur.fetchone()[0]
                self.log_test(
                    f"User '{user}' has CONNECT on '{db}'",
                    has_connect,
                    "Database access",
                )

        cur.close()

    def test_schemas_exist(self, conn):
        """Test that required schemas exist in each database"""
        print(f"\n{BLUE}=== Testing Schemas ==={RESET}")

        # Test identity database schema
        try:
            identity_conn = self.get_user_connection(
                "silentkey_identity",
                "postgres",
                self.passwords["PG_SUPER_PASS"],
            )
            cur = identity_conn.cursor()

            cur.execute(
                """
                SELECT schema_name, schema_owner
                FROM information_schema.schemata
                WHERE schema_name = 'identity'
            """
            )
            result = cur.fetchone()
            exists = result is not None
            self.log_test(f"Schema 'identity' exists in silentkey_identity", exists)

            if exists:
                schema_name, owner = result
                self.log_test(
                    f"Schema 'identity' owned by sk_migration_user",
                    owner == "sk_migration_user",
                    f"Current owner: {owner}",
                )

            cur.close()
            identity_conn.close()
        except Exception as e:
            self.log_test(
                "Connect to silentkey_identity database", False, f"Error: {str(e)}"
            )

        # Test audit database schema
        try:
            audit_conn = self.get_user_connection(
                "silentkey_audit", "postgres", self.passwords["PG_SUPER_PASS"]
            )
            cur = audit_conn.cursor()

            cur.execute(
                """
                SELECT schema_name, schema_owner
                FROM information_schema.schemata
                WHERE schema_name = 'audit'
            """
            )
            result = cur.fetchone()
            exists = result is not None
            self.log_test(f"Schema 'audit' exists in silentkey_audit", exists)

            if exists:
                schema_name, owner = result
                self.log_test(
                    f"Schema 'audit' owned by sk_migration_user",
                    owner == "sk_migration_user",
                    f"Current owner: {owner}",
                )

            cur.close()
            audit_conn.close()
        except Exception as e:
            self.log_test(
                "Connect to silentkey_audit database", False, f"Error: {str(e)}"
            )

    def test_schema_permissions(self):
        """Test schema usage permissions"""
        print(f"\n{BLUE}=== Testing Schema USAGE Permissions ==={RESET}")

        # Test identity schema permissions
        try:
            conn = self.get_user_connection(
                "silentkey_identity",
                "sk_app_user",
                self.passwords["sk_app_password"],
            )
            cur = conn.cursor()

            cur.execute(
                "SELECT has_schema_privilege('sk_app_user', 'identity', 'USAGE')"
            )
            has_usage = cur.fetchone()[0]
            self.log_test(
                "sk_app_user has USAGE on identity schema",
                has_usage,
                "Can access schema",
            )

            cur.execute(
                "SELECT has_schema_privilege('sk_app_user', 'identity', 'CREATE')"
            )
            has_create = cur.fetchone()[0]
            self.log_test(
                "sk_app_user CANNOT CREATE in identity schema",
                not has_create,
                "Security: Prevented from creating objects",
            )

            cur.close()
            conn.close()
        except Exception as e:
            self.log_test(
                "Test identity schema permissions", False, f"Error: {str(e)}"
            )

        # Test audit schema permissions
        try:
            conn = self.get_user_connection(
                "silentkey_audit",
                "sk_readonly_user",
                self.passwords["sk_readonly_password"],
            )
            cur = conn.cursor()

            cur.execute(
                "SELECT has_schema_privilege('sk_readonly_user', 'audit', 'USAGE')"
            )
            has_usage = cur.fetchone()[0]
            self.log_test(
                "sk_readonly_user has USAGE on audit schema",
                has_usage,
                "Can access schema",
            )

            cur.execute(
                "SELECT has_schema_privilege('sk_readonly_user', 'audit', 'CREATE')"
            )
            has_create = cur.fetchone()[0]
            self.log_test(
                "sk_readonly_user CANNOT CREATE in audit schema",
                not has_create,
                "Security: Prevented from creating objects",
            )

            cur.close()
            conn.close()
        except Exception as e:
            self.log_test("Test audit schema permissions", False, f"Error: {str(e)}")

        # Test migration user has CREATE permission
        try:
            conn = self.get_user_connection(
                "silentkey_identity",
                "sk_migration_user",
                self.passwords["sk_migration_password"],
            )
            cur = conn.cursor()

            cur.execute(
                "SELECT has_schema_privilege('sk_migration_user', 'identity', 'CREATE')"
            )
            has_create = cur.fetchone()[0]
            self.log_test(
                "sk_migration_user CAN CREATE in identity schema",
                has_create,
                "Required for migrations",
            )

            cur.close()
            conn.close()
        except Exception as e:
            self.log_test(
                "Test migration user CREATE permission", False, f"Error: {str(e)}"
            )

    def test_public_access_revoked(self, conn):
        """Test that PUBLIC access has been revoked"""
        print(f"\n{BLUE}=== Testing PUBLIC Access Lockdown ==={RESET}")
        cur = conn.cursor()

        databases = ["silentkey_identity", "silentkey_audit"]
        for db in databases:
            cur.execute(
                """
                SELECT pg_catalog.has_database_privilege('public', %s, 'CONNECT')
            """,
                (db,),
            )
            public_can_connect = cur.fetchone()[0]
            self.log_test(
                f"PUBLIC cannot CONNECT to '{db}'",
                not public_can_connect,
                "Security: Default access revoked",
            )

        cur.close()

    def test_default_privileges(self):
        """Test default privileges for future tables"""
        print(f"\n{BLUE}=== Testing Default Privileges ==={RESET}")

        # Test identity database default privileges
        try:
            conn = self.get_user_connection(
                "silentkey_identity",
                "postgres",
                self.passwords["PG_SUPER_PASS"],
            )
            cur = conn.cursor()

            # Check default privileges for tables created by sk_migration_user
            cur.execute(
                """
                SELECT defaclrole::regrole::text, defaclnamespace, defaclobjtype,
                       array_to_string(defaclacl, ',') as privileges
                FROM pg_default_acl
                WHERE defaclrole = 'sk_migration_user'::regrole
                  AND defaclnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'identity')
                  AND defaclobjtype = 'r'
            """
            )
            result = cur.fetchone()
            has_default_privs = result is not None
            self.log_test(
                "Default privileges set for identity schema tables",
                has_default_privs,
                "sk_app_user will get SELECT, INSERT, UPDATE on new tables",
            )

            cur.close()
            conn.close()
        except Exception as e:
            self.log_test(
                "Test identity default privileges", False, f"Error: {str(e)}"
            )

        # Test audit database default privileges
        try:
            conn = self.get_user_connection(
                "silentkey_audit", "postgres", self.passwords["PG_SUPER_PASS"]
            )
            cur = conn.cursor()

            cur.execute(
                """
                SELECT defaclrole::regrole::text, defaclnamespace, defaclobjtype,
                       array_to_string(defaclacl, ',') as privileges
                FROM pg_default_acl
                WHERE defaclrole = 'sk_migration_user'::regrole
                  AND defaclnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'audit')
                  AND defaclobjtype = 'r'
            """
            )
            results = cur.fetchall()
            has_default_privs = len(results) > 0
            self.log_test(
                "Default privileges set for audit schema tables",
                has_default_privs,
                "sk_app_user gets INSERT, sk_readonly_user gets SELECT",
            )

            cur.close()
            conn.close()
        except Exception as e:
            self.log_test("Test audit default privileges", False, f"Error: {str(e)}")

    def print_summary(self):
        """Print test summary"""
        print(f"\n{BLUE}{'=' * 60}{RESET}")
        print(f"{BLUE}TEST SUMMARY{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}")

        total = len(self.test_results)
        passed = sum(1 for _, p, _ in self.test_results if p)
        failed = total - passed

        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {passed}{RESET}")
        if failed > 0:
            print(f"{RED}Failed: {failed}{RESET}")

            print(f"\n{RED}Failed Tests:{RESET}")
            for name, passed, message in self.test_results:
                if not passed:
                    print(f"  ✗ {name}")
                    if message:
                        print(f"    → {message}")
        else:
            print(f"\n{GREEN}🎉 All tests passed!{RESET}")

        print(f"{BLUE}{'=' * 60}{RESET}\n")

        return failed == 0


def main():
    """Main test runner"""
    print(f"{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}SilentKey PostgreSQL Schema Validation{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

    # Check required environment variables
    required_vars = [
        "PG_SUPER_PASS",
        "DB_PASSWORD",
        "MIGRATION_DB_PASSWORD",
        "AUDIT_DB_PASSWORD",
    ]

    alias_map = {
        "DB_PASSWORD": "sk_app_password",
        "MIGRATION_DB_PASSWORD": "sk_migration_password",
        "AUDIT_DB_PASSWORD": "sk_readonly_password",
    }

    missing_vars = [
        var for var in required_vars
        if not os.environ.get(var) and not os.environ.get(alias_map.get(var, ""))
    ]
    if missing_vars:
        print(f"{RED}Error: Missing environment variables:{RESET}")
        for var in missing_vars:
            print(f"  - {var}")
        print(
            f"\n{YELLOW}Please ensure all passwords are set in .env file{RESET}")
        sys.exit(1)

    validator = PostgresSchemaValidator()

    try:
        # Get superuser connection
        conn = validator.get_postgres_connection()

        # Run all tests
        validator.test_databases_exist(conn)
        validator.test_roles_exist(conn)
        validator.test_password_authentication()
        validator.test_database_connect_permissions(conn)
        validator.test_public_access_revoked(conn)
        validator.test_schemas_exist(conn)
        validator.test_schema_permissions()
        validator.test_default_privileges()

        conn.close()

        # Print summary and exit with appropriate code
        success = validator.print_summary()
        sys.exit(0 if success else 1)

    except psycopg.Error as e:
        print(f"{RED}Database connection error: {str(e)}{RESET}")
        print(
            f"{YELLOW}Ensure PostgreSQL is running and credentials are correct{RESET}"
        )
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Unexpected error: {str(e)}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()

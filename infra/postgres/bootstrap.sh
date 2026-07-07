#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------
# SilentKey PostgreSQL Bootstrap (Unix)
# ----------------------------------------

ENV_FILE=".env"
SQL_FILE="infra/postgres/bootstrap.sql"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[ERROR] .env file not found"
  exit 1
fi

if [[ ! -f "$SQL_FILE" ]]; then
  echo "[ERROR] bootstrap.sql not found"
  exit 1
fi

# Load env vars and strip quotes
set -a
while IFS='=' read -r key value; do
  # Skip empty lines and comments
  [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
  
  # Remove leading/trailing whitespace and quotes
  key=$(echo "$key" | xargs)
  value=$(echo "$value" | xargs | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
  
  # Export the variable
  export "$key=$value"
done < "$ENV_FILE"
set +a

if [[ -n "${PG_SUPER_PASS:-}" ]]; then
  export PGPASSWORD="$PG_SUPER_PASS"
fi

# Validate required vars
REQUIRED_VARS=(
  DB_PASSWORD
  MIGRATION_DB_PASSWORD
  AUDIT_DB_PASSWORD
)

LEGACY_VARS=(
  sk_app_password
  sk_migration_password
  sk_readonly_password
)

for index in "${!REQUIRED_VARS[@]}"; do
  var="${REQUIRED_VARS[$index]}"
  legacyVar="${LEGACY_VARS[$index]}"
  value="${!var:-}"
  if [[ -z "$value" ]]; then
    value="${!legacyVar:-}"
  fi
  if [[ -z "$value" ]]; then
    echo "[ERROR] Environment variable $var is not set"
    exit 1
  fi
  
  # Check minimum password length
  if [[ ${#value} -lt 12 ]]; then
    echo "[WARNING] $var is shorter than 12 characters"
  fi
  export "$var=$value"
done

echo "[INFO] Running SilentKey DB bootstrap..."

# Pass passwords as PostgreSQL custom settings (my.* namespace) via PGOPTIONS
PGOPTIONS="-c my.sk_app_password='$DB_PASSWORD' -c my.sk_migration_password='$MIGRATION_DB_PASSWORD' -c my.sk_readonly_password='$AUDIT_DB_PASSWORD'" \
  psql -U postgres -f "$SQL_FILE"

if [[ $? -ne 0 ]]; then
  echo "[FAILED] Database bootstrap failed"
  exit 1
fi

echo "[SUCCESS] Database bootstrap completed"

# Run schema validation tests
echo ""
echo "[INFO] Running schema validation tests..."

# Check if Python is available
if command -v python3 &> /dev/null; then
  python3 tests/pg_schema_check.py
  TEST_EXIT_CODE=$?
  if [[ $TEST_EXIT_CODE -eq 0 ]]; then
    echo ""
    echo "[SUCCESS] All schema validation tests passed!"
  else
    echo ""
    echo "[WARNING] Some schema validation tests failed. Check output above."
    exit $TEST_EXIT_CODE
  fi
elif command -v python &> /dev/null; then
  python tests/pg_schema_check.py
  TEST_EXIT_CODE=$?
  if [[ $TEST_EXIT_CODE -eq 0 ]]; then
    echo ""
    echo "[SUCCESS] All schema validation tests passed!"
  else
    echo ""
    echo "[WARNING] Some schema validation tests failed. Check output above."
    exit $TEST_EXIT_CODE
  fi
else
  echo "[WARNING] Python not found. Skipping schema validation tests."
  echo "To run tests manually: python3 tests/pg_schema_check.py"
fi

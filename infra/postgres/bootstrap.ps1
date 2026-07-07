# ----------------------------------------
# SilentKey PostgreSQL Bootstrap (Windows)
# ----------------------------------------

$EnvFile = ".env"
$SqlFile = "infra\postgres\bootstrap.sql"

if (!(Test-Path $EnvFile)) {
    Write-Error ".env file not found"
    exit 1
}
if (!(Test-Path $SqlFile)) {
    Write-Error "bootstrap.sql not found"
    exit 1
}

# Load .env manually (PowerShell has no native dotenv)
Get-Content $EnvFile | ForEach-Object {
    # Skip empty lines and comments
    if ($_ -match "^\s*#" -or $_ -match "^\s*$") {
        return
    }
    # Match key=value, trim quotes from value
    if ($_ -match "^\s*([^#=]+)=(.+)$") {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim().Trim('"').Trim("'")
        [System.Environment]::SetEnvironmentVariable($key, $value)
    }
}

function Get-EnvValue {
    param(
        [string]$Primary,
        [string]$Legacy
    )

    $primaryValue = [Environment]::GetEnvironmentVariable($Primary)
    if ($primaryValue) {
        return $primaryValue
    }

    $legacyValue = [Environment]::GetEnvironmentVariable($Legacy)
    if ($legacyValue) {
        [System.Environment]::SetEnvironmentVariable($Primary, $legacyValue)
        return $legacyValue
    }

    return $null
}

$AppPassword = Get-EnvValue -Primary "DB_PASSWORD" -Legacy "sk_app_password"
$MigrationPassword = Get-EnvValue -Primary "MIGRATION_DB_PASSWORD" -Legacy "sk_migration_password"
$ReadonlyPassword = Get-EnvValue -Primary "AUDIT_DB_PASSWORD" -Legacy "sk_readonly_password"

$RequiredVars = @(
    @{ Name = "DB_PASSWORD"; Value = $AppPassword },
    @{ Name = "MIGRATION_DB_PASSWORD"; Value = $MigrationPassword },
    @{ Name = "AUDIT_DB_PASSWORD"; Value = $ReadonlyPassword }
)

foreach ($var in $RequiredVars) {
    if (-not $var.Value) {
        Write-Error "Environment variable $($var.Name) is not set"
        exit 1
    }
}

$SuperPassword = Get-EnvValue -Primary "PG_SUPER_PASS" -Legacy "PG_SUPER_PASS"
if ($SuperPassword) {
    $env:PGPASSWORD = $SuperPassword
}

Write-Host "[INFO] Running SilentKey DB bootstrap..."

# Pass passwords as PostgreSQL custom settings (my.* namespace) via PGOPTIONS
$env:PGOPTIONS = "-c my.sk_app_password='$AppPassword' -c my.sk_migration_password='$MigrationPassword' -c my.sk_readonly_password='$ReadonlyPassword'"

psql -U postgres -f $SqlFile

if ($LASTEXITCODE -ne 0) {
    Write-Error "[FAILED] Database bootstrap failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "[SUCCESS] Database bootstrap completed"

# Run schema validation tests
Write-Host "`n[INFO] Running schema validation tests..."

# Check if Python is available
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
}

if ($pythonCmd) {
    & $pythonCmd tests\pg_schema_check.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[SUCCESS] All schema validation tests passed!" -ForegroundColor Green
    } else {
        Write-Warning "`n[WARNING] Some schema validation tests failed. Check output above."
        exit $LASTEXITCODE
    }
} else {
    Write-Warning "[WARNING] Python not found. Skipping schema validation tests."
    Write-Host "To run tests manually: python tests\pg_schema_check.py"
}

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
    if ($_ -match "^\s*([^#=]+)=(.+)$") {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}

$RequiredVars = @(
    "sk_app_password",
    "sk_migration_password",
    "sk_readonly_password"
)

foreach ($var in $RequiredVars) {
    if (-not [Environment]::GetEnvironmentVariable($var)) {
        Write-Error "Environment variable $var is not set"
        exit 1
    }
}

Write-Host "[INFO] Running SilentKey DB bootstrap..."

# Pass passwords as PostgreSQL custom settings (my.* namespace) via PGOPTIONS
$env:PGOPTIONS = "-c my.sk_app_password='$($env:sk_app_password)' -c my.sk_migration_password='$($env:sk_migration_password)' -c my.sk_readonly_password='$($env:sk_readonly_password)'"

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

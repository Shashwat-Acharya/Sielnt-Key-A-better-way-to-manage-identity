#!/usr/bin/env python3
"""
Environment Variable Validation Script
Validates that all required environment variables are set and secure
Run this before starting the application
"""
import sys
from pathlib import Path

try:
    import environs
except ImportError:
    print("❌ ERROR: environs package not installed")
    print("   Install with: pip install environs")
    sys.exit(1)


def validate_env():
    """Validate environment variables"""
    errors = []
    warnings = []
    
    # Load environment variables
    env = environs.Env()
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        env.read_env(str(env_file))
    
    # Required variables
    required_vars = [
        'sk_app_password',
        'sk_migration_password',
        'sk_readonly_password',
        'SECRET_KEY',
    ]
    
    # Check for missing variables
    missing = []
    for var in required_vars:
        try:
            env.str(var)
        except environs.EnvError:
            missing.append(var)
    
    if missing:
        errors.append(f"Missing required environment variables: {', '.join(missing)}")
    
    # Validate SECRET_KEY strength
    try:
        secret_key = env.str('SECRET_KEY')
        if len(secret_key) < 50:
            errors.append("SECRET_KEY must be at least 50 characters long")
        if secret_key == 'CHANGE_ME_TO_50_PLUS_CHARACTER_RANDOM_STRING':
            errors.append("SECRET_KEY is still set to default value - must be changed")
    except environs.EnvError:
        pass  # Already in missing list
    
    # Validate passwords are not defaults
    default_indicators = ['CHANGE_ME', 'password', 'Password123', 'admin']
    for var in ['sk_app_password', 'sk_migration_password', 'sk_readonly_password']:
        try:
            value = env.str(var)
            if any(indicator in value for indicator in default_indicators):
                errors.append(f"{var} appears to be a default/weak password")
            if len(value) < 12:
                warnings.append(f"{var} should be at least 12 characters long")
        except environs.EnvError:
            pass  # Already in missing list
    
    # Check DEBUG setting in production
    debug = env.bool('DEBUG', False)
    if debug:
        warnings.append("DEBUG is enabled - ensure this is intentional (never use in production)")
    
    # Check ALLOWED_HOSTS
    allowed_hosts = env.list('ALLOWED_HOSTS', [])
    if not allowed_hosts and not debug:
        warnings.append("ALLOWED_HOSTS is empty - this may cause issues when DEBUG=False")
    
    # Print results
    print("=" * 60)
    print("SilentKey Environment Validation")
    print("=" * 60)
    
    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"  • {error}")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")
    
    if not errors and not warnings:
        print("\n✅ All environment variables are properly configured!")
    
    print("=" * 60)
    
    if errors:
        sys.exit(1)
    
    return True


if __name__ == '__main__':
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        print(f"Loading environment from: {env_file}")
    else:
        print("⚠️  Warning: .env file not found")
    
    validate_env()

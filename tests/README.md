# Tests

This directory contains automated tests for all components of Silent Key.

## Overview

Comprehensive test suite covering:
- Backend/API tests
- Database schema validation
- Integration tests
- Cross-component tests

## Test Categories

### Current Tests

- **pg_schema_check.py** - PostgreSQL schema validation and testing utility

## Running Tests

### Backend Tests
```bash
cd ../backend
python manage.py test
```

### Database Schema Tests
```bash
python pg_schema_check.py
```

### All Tests (with pytest)
```bash
pytest tests/
```

## Test Structure

Tests use:
- Django TestCase for backend tests
- pytest for integration tests
- Python unittest for utilities

## Coverage

All major components should have:
- Unit tests
- Integration tests
- Edge case coverage

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Pre-release builds

See `.github/workflows/` for CI/CD configuration.

## Related Documentation

- [Main README](../README.md)
- [Backend](../backend/)
- [API Layer](../api/)

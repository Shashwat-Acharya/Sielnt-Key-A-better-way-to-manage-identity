# Infrastructure

This directory contains infrastructure components and deployment configurations for Silent Key.

## Overview

The infrastructure layer provides:
- Database setup and management
- Caching layer configuration
- Container and deployment tools
- Database initialization scripts

## Components

### PostgreSQL
- **postgresql-18.1/** - PostgreSQL 18.1 source code
- **bootstrap.ps1** - PowerShell PostgreSQL initialization script
- **bootstrap.sh** - Shell PostgreSQL initialization script
- **bootstrap.sql** - SQL initialization script for database schema

### Redis
- **redis/** - Redis cache layer (planned/under development)

## Getting Started

### PostgreSQL Setup

#### On Windows (PowerShell):
```powershell
.\postgres\bootstrap.ps1
```

#### On Linux/macOS (Bash):
```bash
./postgres/bootstrap.sh
```

#### Manual SQL Setup:
```sql
psql -U Postgres -f postgres/bootstrap.sql
```

### Configuration

Database connection details should be configured in the application settings:
- Host: localhost (or configured server)
- Port: 5432
- Database: silent_key (or as per bootstrap)

## Services

- **PostgreSQL** - Primary relational database
- **Redis** - Caching and session storage (planned)

## Docker & Deployment

When deploying using Docker, build scripts in this folder should be used.

## Related Documentation

- [Main README](../README.md)
- [Backend](../backend/)
- [API Layer](../api/)

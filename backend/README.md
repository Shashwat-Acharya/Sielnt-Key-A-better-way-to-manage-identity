# Backend

This directory contains the core Django backend application for Silent Key identity management system.

## Overview

The backend provides the central API server for handling identity management, authentication, session management, and integration with subsystems.

## Structure

```
backend/
├── backend/          # Django project configuration
│   ├── settings.py   # Django settings
│   ├── urls.py       # URL routing
│   ├── asgi.py       # ASGI web server application
│   └── wsgi.py       # WSGI web server application
├── identity/         # Core identity management Django app
│   ├── models.py     # Database models
│   ├── views.py      # Request handlers
│   ├── admin.py      # Django admin interface
│   ├── apps.py       # App configuration
│   ├── urls.py       # App-level URL routing
│   └── migrations/   # Database migrations
└── manage.py         # Django management script
```

## Key Components

### backend/
- **settings.py** - Django configuration, database setup, installed apps
- **urls.py** - Main URL routing dispatcher
- **wsgi.py/asgi.py** - Web server interfaces

### identity/
- **models.py** - Core identity, user, and authentication data models
- **views.py** - API endpoint handlers
- **migrations/** - Database schema version control

## Getting Started

### Prerequisites
- Python 3.14+
- PostgreSQL running (configure in settings.py)
- Virtual environment activated

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Apply database migrations:
```bash
python manage.py migrate
```

3. Create superuser:
```bash
python manage.py createsuperuser
```

### Running the Development Server

```bash
python manage.py runserver
```

Server will be available at `http://localhost:8000`

## Configuration

Database and security settings are in `backend/settings.py`. Configure environment variables as needed.

## Testing

```bash
python manage.py test
```

## Related Documentation

- [Main README](../README.md)
- [API Layer](../api/)
- [Infrastructure](../infra/)
- [Tests](../tests/)

"""Database helpers for the standalone API layer.

The API package should not open a connection at import time. Instead, callers
request a connection explicitly and close it deterministically when finished.
"""

from contextlib import contextmanager
from pathlib import Path
import os

import psycopg


def _load_env_file(env_path: Path):
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file(Path(__file__).resolve().parents[1] / '.env')


def _env_str(*names, default=None):
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    return default


DEFAULT_DB_NAME = _env_str("DB_NAME", default="silentkey_identity")
DEFAULT_DB_USER = _env_str("DB_USER", "sk_app_user", default="sk_app_user")
DEFAULT_DB_PASSWORD = _env_str("DB_PASSWORD", "sk_app_password", default="")
DEFAULT_DB_HOST = _env_str("DB_HOST", default="localhost")
DEFAULT_DB_PORT = int(_env_str("DB_PORT", default="5432"))
DEFAULT_CONNECT_TIMEOUT = int(_env_str("DB_CONNECT_TIMEOUT", default="10"))


def build_connection_kwargs(
    *,
    dbname: str = DEFAULT_DB_NAME,
    user: str = DEFAULT_DB_USER,
    password: str = DEFAULT_DB_PASSWORD,
    host: str = DEFAULT_DB_HOST,
    port: int = DEFAULT_DB_PORT,
    connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
):
    return {
        "dbname": dbname,
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "connect_timeout": connect_timeout,
    }


def get_connection(**overrides):
    """Open a PostgreSQL connection using repository environment settings."""
    kwargs = build_connection_kwargs(**overrides)
    return psycopg.connect(**kwargs, autocommit=False)


@contextmanager
def connection_scope(**overrides):
    """Yield a connection and always close it afterward."""
    connection = get_connection(**overrides)
    try:
        yield connection
    finally:
        connection.close()


def close_connection(connection):
    """Close a connection if it is still open."""
    if connection is not None:
        connection.close()
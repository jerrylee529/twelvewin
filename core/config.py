# -*- coding: utf-8 -*-

"""Settings loaded from ``.env`` via ``core.env`` (no Flask app or INI files)."""

import os
from urllib.parse import urlsplit, urlunsplit

from core.env import PROJECT_ROOT, load_dotenv_files

# Ensure .env is loaded before any os.environ reads in this module.
load_dotenv_files()

LOCAL_DATA_DIR = os.path.join(PROJECT_ROOT, 'local_data')


def _normalize_database_url(url):
    if not url:
        return None

    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]

    if url.startswith('postgresql://'):
        url = 'postgresql+psycopg://' + url[len('postgresql://'):]

    if url.startswith('postgresql+psycopg://'):
        parts = urlsplit(url)
        query = '&'.join(
            item for item in parts.query.split('&')
            if item and not item.startswith('channel_binding=')
        )
        return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))

    return url


def _get_bool_env(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    if isinstance(value, str):
        return value.lower() not in ('0', 'false', 'no', 'off')
    return bool(value)


def _env(name, default=None):
    value = os.environ.get(name)
    if value is None:
        return default
    if isinstance(value, str):
        stripped = value.strip()
        if (stripped.startswith("'") and stripped.endswith("'")) or (
            stripped.startswith('"') and stripped.endswith('"')
        ):
            return stripped[1:-1]
    return value


def load_settings_from_env():
    """Build a settings dict from ``.env`` / environment variables."""
    load_dotenv_files()

    day_file_path = _env('DAY_FILE_PATH', os.path.join(LOCAL_DATA_DIR, 'day_data'))
    result_path = _env('RESULT_PATH', os.path.join(LOCAL_DATA_DIR, 'results'))
    if day_file_path and not day_file_path.endswith(os.sep):
        day_file_path = day_file_path + os.sep

    return {
        'SQLALCHEMY_DATABASE_URI': _normalize_database_url(_env('DATABASE_URL')),
        'DAY_FILE_PATH': day_file_path,
        'RESULT_PATH': result_path,
        'RESULT_FILE_PATH': result_path,
        'INDEX_FILE_PATH': _env(
            'INDEX_FILE_PATH',
            os.path.join(LOCAL_DATA_DIR, 'index_data'),
        ),
        'READ_ANALYSIS_FROM_DB': _get_bool_env('READ_ANALYSIS_FROM_DB', True),
        'CSV_DEV_FALLBACK': _get_bool_env('CSV_DEV_FALLBACK', False),
        'DEBUG': _get_bool_env('DEBUG', False),
        'REDIS_URL': _env('REDIS_URL', 'redis://:@127.0.0.1:6379/0'),
        'SECRET_KEY': _env('SECRET_KEY'),
        'SECURITY_PASSWORD_SALT': _env('SECURITY_PASSWORD_SALT'),
        'MAIL_SERVER': _env('APP_MAIL_SERVER', 'smtp.googlemail.com'),
        'MAIL_PORT': int(_env('APP_MAIL_PORT', '465')),
        'MAIL_USE_TLS': _get_bool_env('APP_MAIL_USE_TLS', False),
        'MAIL_USE_SSL': _get_bool_env('APP_MAIL_USE_SSL', True),
        'MAIL_USERNAME': _env('APP_MAIL_USERNAME'),
        'MAIL_PASSWORD': _env('APP_MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': _env('APP_MAIL_DEFAULT_SENDER', 'from@example.com'),
        'STRIPE_SECRET_KEY': _env('STRIPE_SECRET_KEY'),
        'STRIPE_PUBLISHABLE_KEY': _env('STRIPE_PUBLISHABLE_KEY'),
    }


def load_core_settings():
    """Primary settings loader for compute and analysis batch jobs."""
    return load_settings_from_env()

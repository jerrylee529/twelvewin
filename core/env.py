# -*- coding: utf-8 -*-

"""Load configuration from the repository root ``.env`` file."""

import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

VALID_APP_ENVS = frozenset({'local', 'development', 'production', 'test'})

APP_ENV_TO_SETTINGS = {
    'local': 'app.config.LocalConfig',
    'development': 'app.config.DevelopmentConfig',
    'production': 'app.config.ProductionConfig',
    'test': 'app.config.TestingConfig',
}

_dotenv_loaded = False


def get_app_env():
    """Active environment name from ``APP_ENV`` in ``.env`` (default ``local``)."""
    value = (os.environ.get('APP_ENV') or 'local').strip().lower()
    if value not in VALID_APP_ENVS:
        return 'local'
    return value


def default_dotenv_path():
    """Path to the project ``.env`` (override with ``DOTENV_PATH``)."""
    custom = os.environ.get('DOTENV_PATH', '').strip()
    if custom:
        return os.path.abspath(custom)
    return os.path.join(PROJECT_ROOT, '.env')


def resolve_app_settings():
    """Flask config class from ``APP_SETTINGS`` or ``APP_ENV`` in ``.env``."""
    explicit = os.environ.get('APP_SETTINGS', '').strip()
    if explicit:
        return explicit
    return APP_ENV_TO_SETTINGS[get_app_env()]


def load_dotenv_files(*, override=False):
    """Load ``.env`` into ``os.environ`` (idempotent unless ``override=True``)."""
    global _dotenv_loaded

    if _dotenv_loaded and not override:
        return True

    path = default_dotenv_path()
    if not os.path.isfile(path):
        _dotenv_loaded = True
        return False

    try:
        from dotenv import load_dotenv
    except ImportError:
        _dotenv_loaded = True
        return False

    load_dotenv(path, override=override)
    _dotenv_loaded = True
    return True


def reset_dotenv_state():
    """Reset loader state (for tests)."""
    global _dotenv_loaded
    _dotenv_loaded = False

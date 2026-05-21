# -*- coding: utf-8 -*-

"""Environment-based settings without importing the Flask application."""

import configparser
import os

from app.config import _normalize_database_url

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
LOCAL_DATA_DIR = os.path.join(PROJECT_ROOT, 'local_data')


def _resolve_ini_section(parser, preferred_env):
    if preferred_env in parser:
        return preferred_env
    for candidate in (preferred_env, 'local', 'debug', 'development', 'production'):
        if candidate in parser:
            return candidate
    sections = parser.sections()
    return sections[0] if sections else None


def load_settings_from_env():
    """Build a settings dict from environment variables (compute/web shared)."""
    database_url = _normalize_database_url(os.environ.get('DATABASE_URL'))
    day_file_path = os.environ.get(
        'DAY_FILE_PATH',
        os.path.join(LOCAL_DATA_DIR, 'day_data'),
    )
    result_path = os.environ.get(
        'RESULT_PATH',
        os.path.join(LOCAL_DATA_DIR, 'results'),
    )
    if day_file_path and not day_file_path.endswith(os.sep):
        day_file_path = day_file_path + os.sep

    read_from_db = os.environ.get('READ_ANALYSIS_FROM_DB', 'true')
    if isinstance(read_from_db, str):
        read_from_db = read_from_db.lower() not in ('0', 'false', 'no', 'off')

    return {
        'SQLALCHEMY_DATABASE_URI': database_url,
        'DAY_FILE_PATH': day_file_path,
        'RESULT_PATH': result_path,
        'RESULT_FILE_PATH': result_path,
        'READ_ANALYSIS_FROM_DB': read_from_db,
        'DEBUG': os.environ.get('DEBUG', 'false').lower() in ('1', 'true', 'yes'),
    }


def load_settings_from_analysis_ini(config_file_path=None, env=None):
    """Load settings from analysis INI when present."""
    config_file_path = config_file_path or os.environ.get(
        'TW_ANALYSIS_CONFIG_FILE',
        os.path.join(PROJECT_ROOT, 'analysis', 'config.ini'),
    )
    if not os.path.isabs(config_file_path):
        config_file_path = os.path.abspath(config_file_path)

    if not os.path.isfile(config_file_path):
        return None

    parser = configparser.ConfigParser()
    parser.read(config_file_path, encoding='UTF-8')
    env = env or os.environ.get('TW_ANALYSIS_ENV', 'debug')
    section = _resolve_ini_section(parser, env)
    if section is None:
        return None

    day_file_path = parser.get(section, 'DAY_FILE_PATH', fallback='')
    result_path = parser.get(section, 'RESULT_FILE_PATH', fallback='')
    if day_file_path and not day_file_path.endswith(os.sep):
        day_file_path = day_file_path + os.sep

    db_uri = parser.get(section, 'SQLALCHEMY_DATABASE_URI', fallback='')
    if not db_uri:
        db_uri = _normalize_database_url(os.environ.get('DATABASE_URL'))

    return {
        'SQLALCHEMY_DATABASE_URI': _normalize_database_url(db_uri),
        'DAY_FILE_PATH': day_file_path,
        'RESULT_PATH': result_path,
        'RESULT_FILE_PATH': result_path,
        'READ_ANALYSIS_FROM_DB': True,
        'DEBUG': parser.getboolean(section, 'DEBUG', fallback=False),
    }


def load_core_settings():
    """Preferred settings for compute: INI then environment."""
    ini_settings = load_settings_from_analysis_ini()
    if ini_settings is not None:
        env_settings = load_settings_from_env()
        for key, value in env_settings.items():
            if ini_settings.get(key) in (None, '') and value not in (None, ''):
                ini_settings[key] = value
        return ini_settings
    return load_settings_from_env()

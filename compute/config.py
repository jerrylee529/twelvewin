# -*- coding: utf-8 -*-

"""Job configuration from ``.env`` (no Flask app or INI files)."""

import os
from types import SimpleNamespace

from werkzeug.utils import import_string

from core.config import load_core_settings
from core.env import load_dotenv_files

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

load_dotenv_files()


def config_get(config, key, default=None):
    if isinstance(config, dict):
        return config.get(key, default)
    return getattr(config, key, default)


def _namespace_from_dict(settings):
    day_file_path = settings.get('DAY_FILE_PATH') or ''
    result_path = settings.get('RESULT_PATH') or settings.get('RESULT_FILE_PATH') or ''
    instrument_filename = os.path.join(day_file_path, 'instruments.csv')

    index_file_path = settings.get('INDEX_FILE_PATH') or day_file_path

    return SimpleNamespace(
        INSTRUMENT_FILENAME=instrument_filename,
        DAY_FILE_PATH=day_file_path,
        RESULT_PATH=result_path,
        RESULT_FILE_PATH=result_path,
        INDEX_FILE_PATH=index_file_path,
        SQLALCHEMY_DATABASE_URI=settings.get('SQLALCHEMY_DATABASE_URI'),
        READ_ANALYSIS_FROM_DB=settings.get('READ_ANALYSIS_FROM_DB', True),
    )


def load_service_config():
    """Resolve job config from SERVICE_SETTINGS or ``.env``."""
    settings_path = os.environ.get('SERVICE_SETTINGS')
    if settings_path:
        return import_string(settings_path)

    return _namespace_from_dict(load_core_settings())


def load_service_config_dict():
    """Return plain dict for result import and DB sync."""
    config = load_service_config()
    return {
        'DAY_FILE_PATH': config_get(config, 'DAY_FILE_PATH'),
        'RESULT_PATH': config_get(config, 'RESULT_PATH') or config_get(config, 'RESULT_FILE_PATH'),
        'INDEX_FILE_PATH': config_get(config, 'INDEX_FILE_PATH'),
        'READ_ANALYSIS_FROM_DB': config_get(config, 'READ_ANALYSIS_FROM_DB', True),
    }

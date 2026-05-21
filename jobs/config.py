# -*- coding: utf-8 -*-

"""Load service configuration for offline jobs."""

import configparser
import os
import sys
from types import SimpleNamespace

from werkzeug.utils import import_string

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, "analysis")
DEFAULT_ANALYSIS_INI = os.path.join(ANALYSIS_DIR, "config.ini")


def config_get(config, key, default=None):
    if isinstance(config, dict):
        return config.get(key, default)
    return getattr(config, key, default)


def _resolve_ini_section(parser, preferred_env):
    if preferred_env in parser:
        return preferred_env
    for candidate in (preferred_env, "local", "debug", "development", "production"):
        if candidate in parser:
            return candidate
    sections = parser.sections()
    return sections[0] if sections else None


def _namespace_from_paths(day_file_path, result_path, instrument_filename=None):
    day_file_path = day_file_path or ""
    if day_file_path and not day_file_path.endswith(os.sep):
        day_file_path = day_file_path + os.sep

    if instrument_filename is None:
        instrument_filename = os.path.join(day_file_path, "instruments.csv")

    return SimpleNamespace(
        INSTRUMENT_FILENAME=instrument_filename,
        DAY_FILE_PATH=day_file_path,
        RESULT_PATH=result_path,
        RESULT_FILE_PATH=result_path,
    )


def _load_from_analysis_ini():
    config_path = os.environ.get("TW_ANALYSIS_CONFIG_FILE", DEFAULT_ANALYSIS_INI)
    if not os.path.isabs(config_path):
        config_path = os.path.abspath(os.path.join(PROJECT_ROOT, config_path))

    if not os.path.isfile(config_path):
        return None

    parser = configparser.ConfigParser()
    parser.read(config_path, encoding="UTF-8")

    env = os.environ.get("TW_ANALYSIS_ENV", "debug")
    section = _resolve_ini_section(parser, env)
    if section is None:
        return None

    day_file_path = parser.get(section, "DAY_FILE_PATH", fallback="")
    result_path = parser.get(section, "RESULT_FILE_PATH", fallback="")
    instrument = parser.get(section, "INSTRUMENT_FILENAME", fallback="")

    if not instrument:
        instrument = os.path.join(day_file_path, "instruments.csv")

    return _namespace_from_paths(day_file_path, result_path, instrument_filename=instrument)


def _load_from_flask_app():
    os.environ.setdefault("TWELVEWIN_DISABLE_ANALYZER", "1")
    os.environ.setdefault("APP_SETTINGS", "app.config.LocalConfig")

    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)

    from app import app

    day_file_path = app.config.get("DAY_FILE_PATH")
    result_path = app.config.get("RESULT_PATH")
    return _namespace_from_paths(day_file_path, result_path)


def load_service_config():
    """Resolve job config from SERVICE_SETTINGS, analysis INI, or Flask app config."""
    settings = os.environ.get("SERVICE_SETTINGS")
    if settings:
        return import_string(settings)

    ini_config = _load_from_analysis_ini()
    if ini_config is not None:
        return ini_config

    return _load_from_flask_app()

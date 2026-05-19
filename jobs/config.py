# -*- coding: utf-8 -*-

"""Load service configuration for offline jobs."""

import os
import sys
from types import SimpleNamespace

from werkzeug.utils import import_string


def config_get(config, key, default=None):
    if isinstance(config, dict):
        return config.get(key, default)
    return getattr(config, key, default)


def load_service_config():
    """Resolve job config from SERVICE_SETTINGS or analysis INI config."""
    settings = os.environ.get("SERVICE_SETTINGS")
    if settings:
        return import_string(settings)

    analysis_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "analysis"))
    if analysis_dir not in sys.path:
        sys.path.insert(0, analysis_dir)

    from config import config as analysis_config

    return SimpleNamespace(
        INSTRUMENT_FILENAME=os.path.join(
            config_get(analysis_config, "DAY_FILE_PATH", ""),
            "instruments.csv",
        ),
        DAY_FILE_PATH=config_get(analysis_config, "DAY_FILE_PATH"),
        RESULT_PATH=config_get(analysis_config, "RESULT_FILE_PATH"),
        RESULT_FILE_PATH=config_get(analysis_config, "RESULT_FILE_PATH"),
    )

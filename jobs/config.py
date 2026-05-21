# -*- coding: utf-8 -*-

"""Load service configuration for offline jobs (re-export compute.config)."""

from compute.config import config_get, load_service_config

__all__ = ['config_get', 'load_service_config']

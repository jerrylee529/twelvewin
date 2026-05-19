# -*- coding: utf-8 -*-

"""Shared atomic CSV export helpers for analysis scripts."""

import os
import sys
from datetime import date

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from jobs.io import atomic_dataframe_to_csv


def get_result_path(config):
    if isinstance(config, dict):
        return config.get("RESULT_FILE_PATH") or config.get("RESULT_PATH")
    return getattr(config, "RESULT_FILE_PATH", None) or getattr(config, "RESULT_PATH", None)


def atomic_export_pair(
    dataframe,
    result_path,
    title,
    *,
    date_suffix=None,
    required_columns=None,
    **to_csv_kwargs,
):
    """Atomically write ``title_<date>.csv`` and ``title.csv``."""
    if date_suffix is None:
        date_suffix = date.today().strftime("%Y%m%d")

    outputs = []
    for suffix in (date_suffix, None):
        if suffix:
            path = os.path.join(result_path, "{}_{}.csv".format(title, suffix))
        else:
            path = os.path.join(result_path, "{}.csv".format(title))

        atomic_dataframe_to_csv(
            dataframe,
            path,
            required_columns=required_columns,
            **to_csv_kwargs,
        )
        outputs.append(path)

    return outputs

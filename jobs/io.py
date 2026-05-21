# -*- coding: utf-8 -*-

"""Atomic CSV write helpers for offline analysis jobs."""

import csv
import os
import tempfile
from typing import Callable, Iterable, Optional


def validate_csv_columns(path: str, required_columns: Iterable[str]) -> None:
    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError("csv has no header row")
        missing = set(required_columns) - set(reader.fieldnames)
        if missing:
            raise ValueError("csv missing columns: {}".format(", ".join(sorted(missing))))


def atomic_write_file(
    final_path: str,
    write_callback: Callable[[str], None],
    *,
    required_columns: Optional[Iterable[str]] = None,
) -> str:
    """Write to a temp file, validate, then atomically replace the target path."""
    final_path = os.path.abspath(final_path)
    final_dir = os.path.dirname(final_path)
    os.makedirs(final_dir, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", suffix=".csv", dir=final_dir)
    os.close(fd)

    try:
        write_callback(tmp_path)
        if required_columns is not None:
            validate_csv_columns(tmp_path, required_columns)
        os.replace(tmp_path, final_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

    return final_path


def atomic_dataframe_to_csv(
    dataframe,
    final_path: str,
    *,
    required_columns: Optional[Iterable[str]] = None,
    **to_csv_kwargs,
) -> str:
    def _write(tmp_path: str) -> None:
        dataframe.to_csv(tmp_path, **to_csv_kwargs)

    return atomic_write_file(final_path, _write, required_columns=required_columns)


def atomic_append_dataframe_to_csv(
    existing_path: str,
    new_dataframe,
    *,
    required_columns: Optional[Iterable[str]] = None,
    **to_csv_kwargs,
) -> str:
    """Merge new rows into an existing CSV and atomically replace the file."""
    import pandas as pd

    existing_path = os.path.abspath(existing_path)

    def _write(tmp_path: str) -> None:
        if os.path.exists(existing_path):
            existing = pd.read_csv(existing_path)
            combined = pd.concat([existing, new_dataframe], ignore_index=True)
        else:
            combined = new_dataframe
        combined.to_csv(tmp_path, **to_csv_kwargs)

    return atomic_write_file(existing_path, _write, required_columns=required_columns)

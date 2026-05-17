# -*- coding: utf-8 -*-

"""Safe CSV access helpers for generated analysis artifacts."""

import csv
import os
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Optional


@dataclass
class CsvReadResult:
    rows: list
    path: str
    update_time: Optional[str] = None
    missing: bool = False
    error: Optional[str] = None


def resolve_under_base(base_dir: str, filename: str) -> str:
    """Resolve a generated data file path and reject traversal outside base_dir."""
    if not filename:
        raise ValueError("filename must not be empty")

    base_path = os.path.abspath(base_dir)
    target_path = os.path.abspath(os.path.join(base_path, filename))

    if os.path.commonpath([base_path, target_path]) != base_path:
        raise ValueError("filename resolves outside configured data directory")

    return target_path


def format_mtime(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None

    file_mtime = time.localtime(os.stat(path).st_mtime)
    return time.strftime("%Y-%m-%d", file_mtime)


def read_rows(
    base_dir: str,
    filename: str,
    *,
    add_id: bool = False,
    add_update_time: bool = False,
    max_rows: Optional[int] = None,
    encoding: str = "utf-8-sig",
    row_transform: Optional[Callable[[dict], Optional[dict]]] = None,
) -> CsvReadResult:
    """Read a CSV file from a configured data directory.

    Missing files return an empty result instead of raising, which lets routes
    keep their response shape while surfacing data availability through logs.
    """
    path = resolve_under_base(base_dir, filename)

    if not os.path.exists(path):
        return CsvReadResult(rows=[], path=path, missing=True, error="file not found")

    update_time = format_mtime(path)
    rows = []

    try:
        with open(path, "r", encoding=encoding, newline="") as csv_file:
            for raw_row in csv.DictReader(csv_file):
                row = dict(raw_row)

                if row_transform is not None:
                    row = row_transform(row)
                    if row is None:
                        continue

                if add_id:
                    row["id"] = len(rows) + 1

                if add_update_time:
                    row["updateTime"] = update_time

                rows.append(row)

                if max_rows is not None and len(rows) >= max_rows:
                    break
    except Exception as exc:
        return CsvReadResult(rows=[], path=path, update_time=update_time, error=repr(exc))

    return CsvReadResult(rows=rows, path=path, update_time=update_time)


def convert_fields(row: dict, field_types: Iterable[tuple]) -> dict:
    """Convert selected row fields, skipping missing or empty values."""
    for field, conversion in field_types:
        value = row.get(field)
        if value in (None, ""):
            continue
        row[field] = conversion(value)
    return row

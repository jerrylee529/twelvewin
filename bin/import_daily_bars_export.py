#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Import consolidated daily_bars.csv into Postgres ``daily_bars`` table."""

import argparse
import logging
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.env import load_dotenv_files

load_dotenv_files()
os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Import daily_bars export CSV into the database')
    parser.add_argument(
        'csv_path',
        nargs='?',
        default=os.environ.get('TW_DAILY_BARS_CSV_PATH', ''),
        help='path to daily_bars.csv export',
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=int(os.environ.get('TW_IMPORT_DAILY_BARS_CHUNK', '20000')),
    )
    parser.add_argument(
        '--truncate',
        action='store_true',
        default=os.environ.get('TW_IMPORT_DAILY_BARS_TRUNCATE', '').lower()
        in ('1', 'true', 'yes', 'on'),
        help='delete all rows in daily_bars before import',
    )
    args = parser.parse_args(argv)

    if not args.csv_path:
        parser.error('csv_path is required (argument or TW_DAILY_BARS_CSV_PATH)')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )

    from compute.daily_bar_store import import_daily_bars_from_export_csv

    summary = import_daily_bars_from_export_csv(
        args.csv_path,
        chunk_size=args.chunk_size,
        truncate=args.truncate,
    )
    print(summary)
    return 0 if summary.get('status') == 'ok' else 1


if __name__ == '__main__':
    raise SystemExit(main())

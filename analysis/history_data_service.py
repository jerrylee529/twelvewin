# coding=utf8

"""Incremental daily bar download service (persists to Postgres ``daily_bars``)."""

__author__ = 'Administrator'

import logging
import os
import sys

from config import config
from quotation import get_history_data
from instruments import get_all_instrument_codes
from market_calendar import resolve_download_end_date

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from compat import set_display_precision
from core.db import session_scope
from core.day_bars import (
    get_last_trade_dates_bulk,
    normalize_history_frame,
    plan_incremental_downloads,
    upsert_bars_from_dataframe,
)
from core.schema import ensure_analysis_schema
from day_data import write_day_csv_enabled

set_display_precision(2)
logger = logging.getLogger(__name__)

if write_day_csv_enabled():
    from jobs.io import atomic_append_dataframe_to_csv, atomic_dataframe_to_csv


class HistoryDataService:
    def __init__(self, start_date='1990-12-1'):
        self.day_file_path = config.get('DAY_FILE_PATH') or ''
        if self.day_file_path and not self.day_file_path.endswith(os.sep):
            self.day_file_path = self.day_file_path + os.sep
        self.start_date = start_date

    def _day_csv_path(self, code):
        return os.path.join(self.day_file_path, "{}.csv".format(code))

    def _maybe_write_csv(self, code, df_download, data_filename, append):
        if not write_day_csv_enabled():
            return
        csv_kwargs = dict(index=False, float_format='%.2f')
        if append:
            atomic_append_dataframe_to_csv(
                data_filename,
                df_download,
                header=False,
                **csv_kwargs,
            )
        else:
            atomic_dataframe_to_csv(
                df_download,
                data_filename,
                **csv_kwargs,
            )

    def run(self):
        ensure_analysis_schema()

        codes = get_all_instrument_codes()
        if not codes:
            logger.warning('No instrument codes available, skip history download')
            return

        max_codes = int(os.environ.get('TW_HISTORY_MAX_CODES', '0') or '0')
        if max_codes > 0:
            codes = codes[:max_codes]
            logger.info('TW_HISTORY_MAX_CODES=%s, limiting instrument batch', max_codes)

        with session_scope() as session:
            end_date, end_source = resolve_download_end_date(session)
            last_dates = get_last_trade_dates_bulk(session, codes)

        logger.info('history download end_date=%s (source=%s)', end_date, end_source)

        pending, skipped = plan_incremental_downloads(
            codes,
            last_dates,
            self.start_date,
            end_date,
        )

        logger.info(
            'history download plan: total=%s pending=%s already_current=%s',
            len(codes),
            len(pending),
            skipped,
        )

        downloaded = 0
        failed = 0
        total_bars = 0

        with session_scope() as session:
            for index, (code, start_date, last_date) in enumerate(pending, start=1):
                data_filename = self._day_csv_path(code)
                df_download = None

                logger.info(
                    'download %s (%d/%d): %s -> %s',
                    code,
                    index,
                    len(pending),
                    start_date,
                    end_date,
                )

                try:
                    df_download = get_history_data(
                        str(code),
                        start=start_date,
                        end=end_date,
                        autype='qfq',
                        ktype='D',
                    )
                except Exception as exc:
                    logger.warning('download failure for %s: %r', code, exc)
                    failed += 1
                    continue

                df_download = normalize_history_frame(df_download)
                if df_download.empty:
                    logger.warning('no data returned for %s', code)
                    failed += 1
                    continue

                inserted = upsert_bars_from_dataframe(session, code, df_download)
                if inserted == 0:
                    skipped += 1
                    continue

                total_bars += inserted
                downloaded += 1
                logger.info('saved %s bars for %s to daily_bars', inserted, code)

                if write_day_csv_enabled():
                    append_csv = last_date is not None
                    self._maybe_write_csv(code, df_download, data_filename, append_csv)

        logger.info(
            'history download finished: total=%s downloaded=%s skipped=%s failed=%s bars=%s',
            len(codes),
            downloaded,
            skipped,
            failed,
            total_bars,
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    history_data_service = HistoryDataService('2019-1-1')
    history_data_service.run()

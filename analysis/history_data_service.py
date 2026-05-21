# coding=utf8

"""增量下载股票日线历史数据服务。

HistoryDataService 从数据库读取全部股票代码，检查 config['DAY_FILE_PATH'] 下已有
<code>.csv 的最后日期，从下一交易日开始通过 quotation.get_history_data 下载前复权日线，
并追加或新建 CSV 文件。
"""

__author__ = 'Administrator'

import os
import sys
from datetime import timedelta, datetime, date

import pandas as pd
from config import config
from quotation import get_history_data
from models import Instrument, Session
from instruments import get_all_instrument_codes

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from compat import set_display_precision
from jobs.io import atomic_append_dataframe_to_csv, atomic_dataframe_to_csv

set_display_precision(2)


#
class HistoryDataService:
    def __init__(self, start_date='1990-12-1'):
        self.day_file_path = config['DAY_FILE_PATH']
        if self.day_file_path and not self.day_file_path.endswith(os.sep):
            self.day_file_path = self.day_file_path + os.sep
        self.start_date = start_date

    def _day_csv_path(self, code):
        return os.path.join(self.day_file_path, "{}.csv".format(code))

    def run(self):

        codes = get_all_instrument_codes()
        if not codes:
            print("No instrument codes in database, skip history download")
            return

        today = date.today()

        for code in codes:
            data_filename = self._day_csv_path(code)

            print("starting download %s, file path: %s" % (code, data_filename))

            start_date = self.start_date

            if os.path.exists(data_filename):
                try:
                    df = pd.read_csv(data_filename, index_col=['date'])
                    last_date = datetime.strptime(df.index[-1], "%Y-%m-%d") + timedelta(days=1)
                    start_date = last_date.strftime("%Y-%m-%d")
                    print("file %s exists, download data from %s" % (data_filename, start_date))
                except pd.errors.EmptyDataError as pderror:
                    print(repr(pderror))
                    continue
                except Exception as e:
                    print(repr(e))
                    continue

            #end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")

            if start_date == end_date:
                continue

            print("download data, code: %s, startdate: %s, enddate: %s" % (code, start_date, end_date))

            try:
                df_download = get_history_data(str(code), start=start_date, end=end_date, autype='qfq', ktype='D')
            except Exception as e:
                print("download failure, code: %s, exception: %s" % (code, repr(e)))
                continue

            if df_download is not None:
                df_download.sort_index(inplace=True)
                csv_kwargs = dict(index=False, float_format='%.2f')

                if os.path.exists(data_filename):
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


if __name__ == '__main__':
    history_data_service = HistoryDataService('2019-1-1')
    history_data_service.run()


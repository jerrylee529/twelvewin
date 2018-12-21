# coding=utf8

__author__ = 'Administrator'

"""
获取历史数据的服务，以增量方式对历史数据文件进行添加，每天收盘后运行一次
"""

import pandas as pd
from datetime import timedelta, datetime, date
from config import config
from bin.quotation import get_history_data
import tushare as ts
import os
from sqlalchemy import create_engine

# 设置精度
pd.set_option('precision', 2)


#
class HistoryDataService:
    def __init__(self, instrument_filename, day_file_path):
        self.instrument_filename = instrument_filename
        self.day_file_path = day_file_path

    def run(self):
        instruments = pd.read_csv(self.instrument_filename, index_col=False, dtype={'code': object})

        if instruments is None:
            print("Could not find any instruments, exit")
            return

        today = date.today()

        for code in instruments['code']:
            data_filename = "%s/%s.csv" % (self.day_file_path, code)  # 日线数据文件名

            print "starting download %s, file path: %s" % (code, data_filename)

            start_date = "1990-12-01"

            if os.path.exists(data_filename):
                try:
                    df = pd.read_csv(data_filename, index_col=['date'])
                    last_date = datetime.strptime(df.index[-1], "%Y-%m-%d") + timedelta(days=1)
                    start_date = last_date.strftime("%Y-%m-%d")
                    print "file %s exists, download data from %s" % (data_filename, start_date)
                except pd.errors.EmptyDataError:
                    continue
                except Exception, e:
                    print repr(e)
                    continue

            #end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")

            if cmp(start_date, end_date) == 0:
                continue

            print "download data, code: %s, startdate: %s, enddate: %s" % (code, start_date, end_date)

            try:
                df_download = get_history_data(str(code), start=start_date, end=end_date, autype='qfq', ktype='D')
            except Exception, e:
                print "download failure, code: %s, exception: %s" % (code, repr(e))
                continue

            if df_download is not None:
                #
                df_download.sort_index(inplace=True)

                if os.path.exists(data_filename):
                    df_download.to_csv(data_filename, mode='a', header=None, index=False, float_format='%.2f')
                else:
                    df_download.to_csv(data_filename, index=False, float_format='%.2f')


if __name__ == '__main__':
    history_data_service = HistoryDataService(instrument_filename=config.INSTRUMENT_FILENAME,
                                              day_file_path=config.DAY_FILE_PATH)
    history_data_service.run()


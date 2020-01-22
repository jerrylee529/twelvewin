# coding=utf8

__author__ = 'Administrator'

"""
获取历史数据的服务，以增量方式对历史数据文件进行添加，每天收盘后运行一次
"""

import os
from datetime import timedelta, datetime, date

import pandas as pd
from config import config
from quotation import get_history_data
from models import Instrument, Session

# 设置精度
pd.set_option('precision', 2)


#
class HistoryDataService:
    def __init__(self, start_date='1990-12-1'):
        self.day_file_path = config['DAY_FILE_PATH']
        self.start_date = start_date

    def run(self):
        session = Session()

        codes = [item[0] for item in session.query(Instrument.code).all()]

        session.close()

        today = date.today()

        for code in codes:
            data_filename = "%s/%s.csv" % (self.day_file_path, code)  # 日线数据文件名

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
                #
                df_download.sort_index(inplace=True)

                if os.path.exists(data_filename):
                    df_download.to_csv(data_filename, mode='a', header=None, index=False, float_format='%.2f')
                else:
                    df_download.to_csv(data_filename, index=False, float_format='%.2f')


if __name__ == '__main__':
    history_data_service = HistoryDataService('2019-1-1')
    history_data_service.run()


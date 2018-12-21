# coding=utf8

__author__ = 'Administrator'

"""
获取历史数据的服务，以增量方式对历史数据文件进行添加，每天收盘后运行一次
"""

from config import config
import tushare as ts
import numpy as np
import pandas as pd
from models import Report, Session
import time


# 财务数据服务
class FinancialDataService:
    def __init__(self, instrument_filename, day_file_path):
        self.instrument_filename = instrument_filename
        self.day_file_path = day_file_path

    def _value_2_float(self, value):
        if np.isnan(value):
            return None
        else:
            return float(value)

    def _download_report(self, year, season):
        print "download report %d:%d" % (year, season)

        df = pd.DataFrame()

        for i in range(3):
            try:
                df = ts.get_report_data(year, season)
                break
            except IOError:
                time.sleep(600)
                continue

        if (df is not None) and (not df.empty):
            df.drop_duplicates(inplace=True)

            # df = df.where(pd.notnull(df), None)

            session = Session()

            for index, row in df.iterrows():

                if session.query(Report).filter(and_(Report.code==row['code'], Report.year=year, Report.season=season) is not None:
                    continue

                item = Report(row['code'], eps=self._value_2_float(row['eps']),
                                  eps_yoy=self._value_2_float(row['eps_yoy']),
                                  bvps=self._value_2_float(row['bvps']),
                                  roe=self._value_2_float(row['roe']), epcf=self._value_2_float(row['epcf']),
                                  net_profits=self._value_2_float(row['net_profits']),
                                  profits_yoy=self._value_2_float(row['profits_yoy']),
                                  report_date=row['report_date'], year=year, season=season)

                session.add(item)

            session.commit()


    # 获取业绩报告
    def run(self):

        #self._download_report(1999, 4)

        #time.sleep(120)

        #for year in range(2000, 2019, 1):
        for year in range(2018, 2019):
            for season in range(1, 5):
                self._download_report(year, season)

if __name__ == '__main__':
    financial_data_service = FinancialDataService(instrument_filename=config.INSTRUMENT_FILENAME,
                                                  day_file_path=config.DAY_FILE_PATH)
    financial_data_service.run()


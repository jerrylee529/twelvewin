# -*- coding:utf-8 -*-

__author__ = 'Administrator'

"""
 年终总结:
 技术面
 1. 最牛公司前十
 2. 最熊公司前十
 3. 最牛行业前十
 4. 最熊行业前十
 5. 各行业中最牛前十
 6. 各行业中最熊前十
 7. 振幅前十
 8. 振幅后十

 基本面
 1. 公司净利率前十
 2. 公司现金分红率前十
 3.
"""





import tushare as ts
import pandas as pd
import os
from datetime import timedelta, datetime, date
import time
from config import config

# 设置精度
pd.set_option('precision', 2)


def format_float(value):
    return round(value, 2)


class Computer(object):
    def __init__(self):
        self.result_list = {}

    def compute(self, code, data):
        pass


class StockInfo(object):
    def __init__(self, industry, code):
        self.industry = industry
        self.code = code
        self.change_rate = -9999  # 涨跌幅
        self.amplitude = -9999  # 振幅，最高到最低价的范围
        self.close_prev_year = -9999  # 前收
        self.open = -9999
        self.close = -9999
        self.high = -9999
        self.low = -9999
        self.pe = -9999
        self.pb = -9999

    def __str__(self):
        return "industry: {}, code: {}, change_rate: {}, amplitude: {}, prev_close: {}, open: {}, close: {}, high: {}, low: {}".format(self.industry, self.code,
                                                                               self.change_rate, self.amplitude, self.close_prev_year, self.open, self.close, self.high, self.low)


# 技术面分析
class TechniqueReport(Computer):

    def compute(self, industry, code, close_prev_year, data):
        if len(data) <= 0:
            return

        stock_info = StockInfo(industry, code)

        low = data['close'].min()
        high = data['close'].max()

        close_last = data.iloc[len(data)-1]['close']

        stock_info.change_rate = format_float((close_last - close_prev_year)*100/close_prev_year)
        stock_info.close_prev_year = format_float(close_prev_year)
        stock_info.low = format_float(low)
        stock_info.high = format_float(high)
        stock_info.open = format_float(data.iloc[0]['open'])
        stock_info.close = format_float(data.iloc[len(data)-1]['close'])
        stock_info.amplitude = format_float((high-low)*100/low)

        self.result_list[code] = stock_info


# 行业分析
class IndustryInfo(object):
    def __init__(self, industry):
        self.industry = industry
        self.avg_change_rate = -9999
        self.avg_amplitude = -9999
        self.avg_price = -9999
        self.avg_pe = -9999
        self.avg_pb = -9999
        self.stock_number = 0

    def __str__(self):
        return "industry: {}, avg_change_rate: {}, avg_amplitude: {}, avg_price: {}, stock_num: {}".format(self.industry,
                                                                                            self.avg_change_rate, self.avg_amplitude, self.avg_price, self.stock_number)


class IndustryReport(Computer):
    def __init__(self):
        self.result_list = {}
        self._total_amplitude = {}
        self._total_change_rate = {}
        self._total_price = {}
        self._total_high = {}
        self._total_low = {}
        self._stock_number = {}

    def compute(self, data):
        for item in data.values():
            if not self.result_list.has_key(item.industry):
                industry_info = IndustryInfo(item.industry)
                self.result_list[item.industry] = industry_info
                self._total_amplitude[item.industry] = 0
                self._total_change_rate[item.industry] = 0
                self._total_price[item.industry] = 0
                self._total_high[item.industry] = 0
                self._total_low[item.industry] = 0
                self._stock_number[item.industry] = 0
            else:
                industry_info = self.result_list[item.industry]

            self._total_amplitude[item.industry] += item.amplitude
            self._total_change_rate[item.industry] += item.change_rate
            self._total_price[item.industry] += item.close
            self._total_high[item.industry] += item.high
            self._total_low[item.industry] += item.low
            self._stock_number[item.industry] += 1

            industry_info.avg_change_rate = format_float(self._total_change_rate[item.industry]/self._stock_number[item.industry])
            industry_info.avg_amplitude = format_float(self._total_amplitude[item.industry]/self._stock_number[item.industry])
            industry_info.avg_price = format_float(self._total_price[item.industry]/self._stock_number[item.industry])
            industry_info.stock_number = self._stock_number[item.industry]


def save_report(filename, result_list):
    dict_list = []
    for item in result_list:
        dict_list.append(item.__dict__)

    df = pd.DataFrame(dict_list)

    df.to_csv(filename, index=False)


def compute(instrument_filename, day_file_path, result_file_path, year):
    instruments = pd.read_csv(instrument_filename, index_col=False, dtype={'code': object})

    if instruments is None:
        print("Could not find any instruments, exit")
        return

    instruments['close'] = None

    technique_report = TechniqueReport()

    code_index = -1
    for index, row in instruments.iterrows():
        code = row['code']
        industry = row['industry']

        data_filename = "%s/%s.csv" % (day_file_path, code)  # 日线数据文件名

        code_index += 1

        print "calculate %s, file path: %s" % (code, data_filename)

        if os.path.exists(data_filename):
            try:
                df = pd.read_csv(data_filename, index_col=False)

                df['date'] = pd.to_datetime(df['date'])  # 将数据类型转换为日期类型
                df = df.set_index('date')  # 将date设置为index

                prev_year = year - 1

                df_year = df[str(year)]

                try:
                    df_prev_year = df[str(prev_year)]
                    last_close = df_prev_year.iloc[len(df_prev_year)-1]['close']
                except Exception, e:
                    print repr(e)
                    last_close = df_year.iloc[0]['open']

                technique_report.compute(industry, code, last_close, df_year)
            except Exception, e:
                print repr(e)
                continue

    save_report(result_file_path + "/annual_technique_report_" + str(year) + ".csv", technique_report.result_list.values())

    for item in technique_report.result_list.values():
        print item.__dict__

    industry_report = IndustryReport()
    industry_report.compute(technique_report.result_list)

    for industry in industry_report.result_list.values():
        print industry.__dict__

    save_report(result_file_path + "/annual_industry_report_" + str(year) + ".csv", industry_report.result_list.values())


if __name__ == '__main__':
    compute(instrument_filename=config.INSTRUMENT_FILENAME, day_file_path=config.DAY_FILE_PATH,
            result_file_path=config.RESULT_PATH, year=2018)
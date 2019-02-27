# coding=utf8

__author__ = 'Administrator'

"""
定时任务管理器
"""

from datetime import datetime
from history_data_service import HistoryDataService
from technical_analysis_service import highest_in_history, ma_long_history, above_ma, break_ma, lowest_in_history
import logging
import os
import sys
sys.path.append("..")
from app.util import string_to_obj


# 输出时间
def job():
    #print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    service_config = string_to_obj(os.environ['SERVICE_SETTINGS'])

    print "start downloading history data, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    history_data_service = HistoryDataService(instrument_filename=service_config.INSTRUMENT_FILENAME,
                                              day_file_path=service_config.DAY_FILE_PATH)
    history_data_service.run()

    print "compute equities that price is highest in history, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    highest_in_history(instrument_filename=service_config.INSTRUMENT_FILENAME, day_file_path=service_config.DAY_FILE_PATH,
                       result_file_path=service_config.RESULT_PATH)

    print "compute equities that price is lowest in history, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    lowest_in_history(instrument_filename=service_config.INSTRUMENT_FILENAME, day_file_path=service_config.DAY_FILE_PATH, result_file_path=service_config.RESULT_PATH)

    print "compute equities that ma is long, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    ma_long_history(instrument_filename=service_config.INSTRUMENT_FILENAME, day_file_path=service_config.DAY_FILE_PATH,
                    result_file_path=service_config.RESULT_PATH, ma1=5, ma2=10, ma3=20)

    print "compute equities that break ma, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    break_ma(instrument_filename=service_config.INSTRUMENT_FILENAME, day_file_path=service_config.DAY_FILE_PATH,
             result_file_path=service_config.RESULT_PATH, ma1=20)

    print "compute equities that above ma, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    above_ma(instrument_filename=service_config.INSTRUMENT_FILENAME, day_file_path=service_config.DAY_FILE_PATH,
             result_file_path=service_config.RESULT_PATH, ma1=250)


if __name__ == '__main__':
    job()

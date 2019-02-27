# coding=utf8

__author__ = 'Administrator'

"""
定时任务管理器
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from history_data_service import HistoryDataService
from technical_analysis_service import highest_in_history, lowest_in_history, ma_long_history, above_ma, break_ma
import logging
import os
import sys
sys.path.append("..")

import getvaluation as gv
import get_value_4_business as gv4b
from instruments import get_instrument_list
from utils.util import string_to_obj
from strategy_test import PEMAStrategy


# 输出时间
def job():
    #print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    service_config = string_to_obj(os.environ['SERVICE_SETTINGS'])

    get_instrument_list(service_config)

    print "start downloading history data, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    history_data_service = HistoryDataService(instrument_filename=service_config.INSTRUMENT_FILENAME,
                                              day_file_path=service_config.DAY_FILE_PATH)
    history_data_service.run()

    print "compute equities that price is highest in history, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    highest_in_history(instrument_filename=service_config.INSTRUMENT_FILENAME, day_file_path=service_config.DAY_FILE_PATH,
                       result_file_path=service_config.RESULT_PATH)

    print "compute equities that price is lowest in history, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    lowest_in_history(instrument_filename=service_config.INSTRUMENT_FILENAME, day_file_path=service_config.DAY_FILE_PATH,
                      result_file_path=service_config.RESULT_PATH)

    print "compute equities that ma is long, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    ma_long_history(instrument_filename=service_config.INSTRUMENT_FILENAME, day_file_path=service_config.DAY_FILE_PATH,
                    result_file_path=service_config.RESULT_PATH, ma1=5, ma2=10, ma3=20)

    print "compute equities that break ma, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    break_ma(instrument_filename=service_config.INSTRUMENT_FILENAME, day_file_path=service_config.DAY_FILE_PATH,
             result_file_path=service_config.RESULT_PATH, ma1=20)

    print "compute equities that above ma, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    above_ma(instrument_filename=service_config.INSTRUMENT_FILENAME, day_file_path=service_config.DAY_FILE_PATH,
             result_file_path=service_config.RESULT_PATH, ma1=250)

    strategy = PEMAStrategy(service_config.DAY_FILE_PATH)

    buy_list, sell_list = strategy.run()

    print buy_list, sell_list

    #gv.get_profit_report()

    #gv4b.get_profit_report()

if __name__ == '__main__':

    '''

    log = logging.getLogger('apscheduler.executors.default')
    log.setLevel(logging.INFO)  # DEBUG

    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    h = logging.StreamHandler()
    h.setFormatter(fmt)
    log.addHandler(h)
    '''
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datafmt='%a, %d %b %Y %H:%M:%S', filename='/tmp/log.txt', filemode='a')

    # BlockingScheduler
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'cron', day_of_week='tue-sat', hour=00, minute=00)
    scheduler.start()

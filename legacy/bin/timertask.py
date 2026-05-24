# -*- coding:utf-8 -*-

"""
定时触发估值和精选股报表生成任务。

脚本持续运行并每秒检查当前时间；在非周末的 20:00:00 执行 getvaluation.py 和
get_value_4_business.py。gettimetowait 是早期按目标时间计算等待秒数的辅助函数，
当前主循环未使用 Timer，而是直接轮询系统时间。
"""

__author__ = 'jerry'

from threading import Timer
import time
from datetime import datetime, timedelta
import os

SECONDS_PER_DAY = 24 * 60 * 60

def gettimetowait(hour, minute, second):
    curTime = datetime.now()
    desTime = curTime.replace(hour=hour, minute=minute, second=second, microsecond=0)
    delta = curTime - desTime
    skipSeconds = SECONDS_PER_DAY - delta.total_seconds()
    #skipSeconds = delta.total_seconds()
    print "Must sleep %d seconds" % skipSeconds
    return skipSeconds

timer_interval = 1

def delayrun():
    print "start running"
    os.system('python getvaluation.py')
    os.system('python get_value_4_business.py')
    print "restart completed"

print "Running......"

while True:
    #print "waitting......"
    current_time = time.localtime(time.time())
    if((current_time.tm_hour == 20) and (current_time.tm_min == 00) and (current_time.tm_sec == 00)
       and (current_time.tm_wday != 0) and (current_time.tm_wday != 6)):
        delayrun()
    time.sleep(1)


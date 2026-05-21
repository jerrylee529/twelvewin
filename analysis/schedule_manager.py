# coding=utf8

"""基于 APScheduler 的日终分析任务调度器。

job() 与 schedule_job.py 类似，负责股票代码更新、历史数据下载、技术分析 CSV 生成和
PEMAStrategy 执行。直接运行时注册 BlockingScheduler，在周二到周六 00:00 执行 job。
"""

__author__ = 'Administrator'

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import logging
import os
import sys


def job():
    """Run the unified end-of-day pipeline (see jobs.eod_all)."""
    _project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)

    os.environ.setdefault("TWELVEWIN_DISABLE_ANALYZER", "1")

    from jobs.eod_all import run_eod_all

    print("starting eod_all at %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return run_eod_all()

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

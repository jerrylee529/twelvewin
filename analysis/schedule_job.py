# coding=utf8

"""日终分析任务编排器（兼容入口）。

新代码请使用 ``python -m jobs.run daily_pipeline`` 或 ``manage.py run_job daily_pipeline``。
"""

from datetime import datetime
import logging
import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')

logger = logging.getLogger(__name__)


def job():
    from jobs.daily_pipeline import run_daily_pipeline

    logger.info("starting daily pipeline at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return run_daily_pipeline()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    job()

# -*- coding: utf-8 -*-

"""CLI: python -m compute <job_name>"""

import argparse
import logging
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.env import load_dotenv_files

load_dotenv_files()
os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')


def _configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description='Run twelvewin offline compute jobs')
    parser.add_argument(
        'job_name',
        choices=[
            'daily_pipeline',
            'ranking_pipeline',
            'cluster_pipeline',
            'finance_profile_pipeline',
            'eod_all',
            'import_results',
            'import_day_bars',
            'annual_pipeline',
        ],
        help='pipeline to execute',
    )
    args = parser.parse_args(argv)
    _configure_logging()

    if args.job_name == 'daily_pipeline':
        from jobs.daily_pipeline import run_daily_pipeline

        run_daily_pipeline()
        return 0

    if args.job_name == 'ranking_pipeline':
        from jobs.ranking_pipeline import run_ranking_pipeline

        run_ranking_pipeline()
        return 0

    if args.job_name == 'cluster_pipeline':
        from jobs.cluster_pipeline import run_cluster_pipeline

        run_cluster_pipeline()
        return 0

    if args.job_name == 'finance_profile_pipeline':
        from jobs.finance_profile_pipeline import run_finance_profile_pipeline

        run_finance_profile_pipeline()
        return 0

    if args.job_name == 'eod_all':
        from jobs.eod_all import run_eod_all

        run_eod_all()
        return 0

    if args.job_name == 'import_results':
        from compute.config import load_service_config_dict
        from compute.result_store import sync_all_results_to_db

        summary = sync_all_results_to_db(load_service_config_dict())
        for key, value in summary.items():
            print('{}: {}'.format(key, value))
        return 0

    if args.job_name == 'annual_pipeline':
        from jobs.annual_pipeline import run_annual_pipeline

        run_annual_pipeline()
        return 0

    if args.job_name == 'import_day_bars':
        from compute.config import load_service_config_dict
        from compute.daily_bar_store import import_day_bars_from_csv

        max_codes = int(os.environ.get('TW_IMPORT_DAY_BARS_MAX_CODES', '0') or '0')
        summary = import_day_bars_from_csv(
            load_service_config_dict(),
            max_codes=max_codes,
        )
        print(summary)
        return 0

    parser.error('unknown job: {}'.format(args.job_name))
    return 1


if __name__ == '__main__':
    raise SystemExit(main())

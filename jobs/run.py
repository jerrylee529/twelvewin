# -*- coding: utf-8 -*-

"""CLI entry point for offline jobs."""

import argparse
import logging
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("TWELVEWIN_DISABLE_ANALYZER", "1")


def _configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run twelvewin offline jobs")
    parser.add_argument(
        "job_name",
        choices=["daily_pipeline"],
        help="job to execute",
    )
    args = parser.parse_args(argv)

    _configure_logging()

    if args.job_name == "daily_pipeline":
        from jobs.daily_pipeline import run_daily_pipeline

        run_daily_pipeline()
        return 0

    parser.error("unknown job: {}".format(args.job_name))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

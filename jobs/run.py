# -*- coding: utf-8 -*-

"""CLI entry point for offline jobs (delegates to compute)."""

import logging
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.env import load_dotenv_files

load_dotenv_files()
os.environ.setdefault("TWELVEWIN_DISABLE_ANALYZER", "1")


def _configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


def main(argv=None):
    if argv is None and len(sys.argv) > 1:
        argv = sys.argv[1:]
    elif argv is None:
        argv = []

    _configure_logging()
    print("Note: prefer: python -m compute <job_name>", file=sys.stderr)

    from compute.__main__ import main as compute_main

    return compute_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-

import datetime
import unittest

from core.day_bars import plan_incremental_downloads


class HistoryDownloadPlanTestCase(unittest.TestCase):
    def test_plan_marks_current_codes_as_skipped(self):
        end_date = '2026-05-22'
        last_dates = {
            '600000': datetime.date(2026, 5, 21),
            '000001': datetime.date(2026, 5, 22),
        }

        pending, skipped = plan_incremental_downloads(
            ['600000', '000001'],
            last_dates,
            '1990-12-01',
            end_date,
        )

        self.assertEqual(1, skipped)
        self.assertEqual(1, len(pending))
        self.assertEqual('600000', pending[0][0])
        self.assertEqual('2026-05-22', pending[0][1])

    def test_plan_queues_codes_needing_one_more_day(self):
        end_date = '2026-05-22'
        last_dates = {'600000': datetime.date(2026, 5, 21)}

        pending, skipped = plan_incremental_downloads(
            ['600000'],
            last_dates,
            '1990-12-01',
            end_date,
        )

        self.assertEqual(0, skipped)
        self.assertEqual(1, len(pending))
        self.assertEqual('600000', pending[0][0])
        self.assertEqual('2026-05-22', pending[0][1])

    def test_plan_queues_new_codes_from_default_start(self):
        pending, skipped = plan_incremental_downloads(
            ['300001'],
            {},
            '2019-01-01',
            '2026-05-24',
        )

        self.assertEqual(0, skipped)
        self.assertEqual(1, len(pending))
        self.assertEqual('300001', pending[0][0])
        self.assertEqual('2019-01-01', pending[0][1])
        self.assertIsNone(pending[0][2])


if __name__ == '__main__':
    unittest.main()

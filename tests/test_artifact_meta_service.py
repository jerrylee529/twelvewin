# -*- coding: utf-8 -*-

import os
import tempfile
import time
import unittest

from app.services.artifact_meta_service import get_artifact_update_time


class ArtifactMetaServiceTestCase(unittest.TestCase):
    def test_get_artifact_update_time_reads_ranking_file_mtime(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "stock_pe.csv")
            with open(csv_path, "w", encoding="utf-8") as handle:
                handle.write("code,name,per\n000001,Ping An,10.5\n")

            update_time = get_artifact_update_time(
                {"RESULT_PATH": tmpdir},
                ranking_key="pe",
            )

        self.assertIsNotNone(update_time)

    def test_get_artifact_update_time_returns_none_for_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            update_time = get_artifact_update_time(
                {"RESULT_PATH": tmpdir},
                technical_key="highest",
            )

        self.assertIsNone(update_time)


if __name__ == "__main__":
    unittest.main()

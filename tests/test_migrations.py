# -*- coding: utf-8 -*-

import os
import unittest

from app import NullAnalyzer, migrate
import app as app_module


class MigrationSetupTestCase(unittest.TestCase):
    def test_migration_scaffold_exists(self):
        self.assertTrue(os.path.exists("migrations/env.py"))
        self.assertTrue(os.path.exists("migrations/script.py.mako"))
        self.assertTrue(os.path.exists("migrations/versions"))
        self.assertTrue(os.path.exists("migrations/versions/33e7716425a6_baseline_schema.py"))
        self.assertTrue(os.path.exists("migrations/versions/b8f4a2c91d0e_add_analysis_job_run.py"))
        self.assertTrue(os.path.exists("migrations/versions/c7e2a9f41b30_phase6_analysis_results.py"))

    def test_flask_migrate_extension_is_optional(self):
        self.assertTrue(migrate is None or migrate.__class__.__name__ == "Migrate")

    def test_disable_analyzer_env_switch_uses_null_analyzer(self):
        # manage.py test sets TWELVEWIN_DISABLE_ANALYZER=1 before app import.
        self.assertIsInstance(app_module.analyzer, NullAnalyzer)


if __name__ == "__main__":
    unittest.main()

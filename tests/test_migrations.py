# -*- coding: utf-8 -*-

import os
import unittest
import importlib
from unittest import mock

from app import migrate


class MigrationSetupTestCase(unittest.TestCase):
    def test_migration_scaffold_exists(self):
        self.assertTrue(os.path.exists("migrations/env.py"))
        self.assertTrue(os.path.exists("migrations/script.py.mako"))
        self.assertTrue(os.path.exists("migrations/versions"))
        self.assertTrue(os.path.exists("migrations/versions/33e7716425a6_baseline_schema.py"))

    def test_flask_migrate_extension_is_optional(self):
        self.assertTrue(migrate is None or migrate.__class__.__name__ == "Migrate")

    def test_disable_analyzer_env_switch_uses_null_analyzer(self):
        import app as app_module

        with mock.patch.dict(os.environ, {"TWELVEWIN_DISABLE_ANALYZER": "1"}):
            reloaded = importlib.reload(app_module)

        self.assertEqual("NullAnalyzer", reloaded.analyzer.__class__.__name__)
        importlib.reload(app_module)


if __name__ == "__main__":
    unittest.main()

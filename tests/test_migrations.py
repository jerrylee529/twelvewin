# -*- coding: utf-8 -*-

import os
import unittest

from app import migrate


class MigrationSetupTestCase(unittest.TestCase):
    def test_migration_scaffold_exists(self):
        self.assertTrue(os.path.exists("migrations/env.py"))
        self.assertTrue(os.path.exists("migrations/script.py.mako"))
        self.assertTrue(os.path.exists("migrations/versions"))

    def test_flask_migrate_extension_is_optional(self):
        self.assertTrue(migrate is None or migrate.__class__.__name__ == "Migrate")


if __name__ == "__main__":
    unittest.main()

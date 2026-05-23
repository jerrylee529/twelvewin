# -*- coding: utf-8 -*-

import os
import unittest
from unittest import mock

from core.env import resolve_app_settings


class EnvMappingTestCase(unittest.TestCase):
    def test_resolve_app_settings_from_app_env(self):
        with mock.patch.dict(os.environ, {'APP_ENV': 'production'}, clear=False):
            os.environ.pop('APP_SETTINGS', None)
            self.assertEqual(
                'app.config.ProductionConfig',
                resolve_app_settings(),
            )

    def test_explicit_app_settings_wins(self):
        with mock.patch.dict(
            os.environ,
            {
                'APP_ENV': 'local',
                'APP_SETTINGS': 'app.config.TestingConfig',
            },
            clear=False,
        ):
            self.assertEqual('app.config.TestingConfig', resolve_app_settings())


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-

import os
import unittest
from unittest import mock

os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')

from compute.config import load_service_config, load_service_config_dict
from core.config import load_core_settings


class ComputeConfigTestCase(unittest.TestCase):
    def test_load_core_settings_from_env(self):
        with mock.patch.dict(
            os.environ,
            {
                'DATABASE_URL': 'postgresql://user:pass@example.com/db?sslmode=require',
                'DAY_FILE_PATH': '/tmp/day/',
                'RESULT_PATH': '/tmp/results',
            },
            clear=False,
        ):
            from core.db import reset_engine

            reset_engine()
            settings = load_core_settings()
            self.assertIn('postgresql+psycopg://', settings['SQLALCHEMY_DATABASE_URI'])
            self.assertTrue(settings['DAY_FILE_PATH'].endswith('/'))
            self.assertEqual('/tmp/results', settings['RESULT_PATH'])

    def test_load_service_config_dict_has_result_path(self):
        config = load_service_config_dict()
        self.assertIn('RESULT_PATH', config)


if __name__ == '__main__':
    unittest.main()

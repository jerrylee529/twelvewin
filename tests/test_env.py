# -*- coding: utf-8 -*-

import os
import tempfile
import unittest
from unittest import mock

from core.env import (
    default_dotenv_path,
    get_app_env,
    load_dotenv_files,
    reset_dotenv_state,
)

try:
    import dotenv  # noqa: F401
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False


@unittest.skipUnless(HAS_DOTENV, 'python-dotenv is not installed')
class EnvLoaderTestCase(unittest.TestCase):
    def setUp(self):
        reset_dotenv_state()

    def tearDown(self):
        reset_dotenv_state()
        for key in (
            'TWELVEWIN_TEST_ENV_MARKER',
            'APP_ENV',
            'DOTENV_PATH',
        ):
            os.environ.pop(key, None)

    def test_load_dotenv_files_reads_project_env(self):
        fd, path = tempfile.mkstemp(suffix='.env')
        os.close(fd)
        try:
            with open(path, 'w', encoding='utf-8') as handle:
                handle.write(
                    'APP_ENV=production\n'
                    'TWELVEWIN_TEST_ENV_MARKER=loaded-from-dotenv\n'
                )

            with mock.patch.dict(os.environ, {'DOTENV_PATH': path}, clear=False):
                reset_dotenv_state()
                self.assertTrue(load_dotenv_files())
                self.assertEqual('production', get_app_env())
                self.assertEqual(
                    'loaded-from-dotenv',
                    os.environ.get('TWELVEWIN_TEST_ENV_MARKER'),
                )
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_default_dotenv_path_points_to_repo_env(self):
        self.assertTrue(default_dotenv_path().endswith('.env'))


if __name__ == '__main__':
    unittest.main()

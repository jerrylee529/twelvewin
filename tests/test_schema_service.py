# -*- coding: utf-8 -*-

import os
import tempfile
import unittest

os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')

import app as app_module
from sqlalchemy import inspect, text

from app.services.schema_service import ensure_analysis_schema, missing_analysis_tables


class SchemaServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app_module.app
        self.db = app_module.db
        self._prev_uri = self.app.config.get('SQLALCHEMY_DATABASE_URI')
        fd, self._db_path = tempfile.mkstemp(suffix='.sqlite')
        os.close(fd)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self._db_path
        self._context = self.app.app_context()
        self._context.push()
        self.db.engine.dispose()
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        self.db.engine.dispose()
        self._context.pop()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = self._prev_uri
        if os.path.exists(self._db_path):
            os.remove(self._db_path)

    def test_missing_analysis_tables_detects_gaps(self):
        missing = missing_analysis_tables(self.db.engine)
        self.assertEqual(missing, [])

    def test_ensure_analysis_schema_creates_dropped_job_run_table(self):
        self.db.session.execute(text('DROP TABLE IF EXISTS analysis_job_run'))
        self.db.session.commit()
        self.assertIn('analysis_job_run', missing_analysis_tables(self.db.engine))

        applied = ensure_analysis_schema()
        self.assertTrue(applied)
        self.assertIn('analysis_job_run', inspect(self.db.engine).get_table_names())


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-

import datetime
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.db.models import Base, FilingDocument
from compute.filing_store import (
    CHECKPOINT_VERSION,
    count_extractable_filings,
    load_sync_checkpoint,
    reset_stuck_filing_extractions,
    save_sync_checkpoint,
)


class FilingStoreCheckpointTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.checkpoint_path = os.path.join(self.temp_dir.name, 'filing_sync_checkpoint.json')

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load_checkpoint(self):
        save_sync_checkpoint('marker-1', code='000001', path=self.checkpoint_path)
        self.assertEqual('marker-1', load_sync_checkpoint(self.checkpoint_path, code='000001'))

        with open(self.checkpoint_path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
        self.assertEqual(CHECKPOINT_VERSION, payload['version'])
        self.assertEqual('000001', payload['code'])

    def test_load_checkpoint_ignores_mismatched_code(self):
        save_sync_checkpoint('marker-1', code='000001', path=self.checkpoint_path)
        self.assertIsNone(load_sync_checkpoint(self.checkpoint_path, code='000002'))

    def test_clear_checkpoint(self):
        save_sync_checkpoint('marker-1', path=self.checkpoint_path)
        save_sync_checkpoint(None, path=self.checkpoint_path)
        self.assertFalse(os.path.exists(self.checkpoint_path))


class FilingStoreResumeTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.now = datetime.datetime.now()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def _add_filing(self, code: str, status: str) -> FilingDocument:
        session = self.session_factory()
        row = FilingDocument(
            code=code,
            year=2024,
            season=0,
            report_kind='annual',
            report_type_label='年报',
            qiniu_key=f'{code}_年报_2024_20250315.pdf',
            filename=f'{code}_年报_2024_20250315.pdf',
            analysis_status=status,
            synced_at=self.now,
        )
        session.add(row)
        session.commit()
        session.close()
        return row

    @patch('compute.filing_store.session_scope')
    def test_reset_stuck_filing_extractions(self, mock_session_scope):
        self._add_filing('000001', FilingDocument.STATUS_PROCESSING)
        self._add_filing('000002', FilingDocument.STATUS_PENDING)

        session = self.session_factory()
        mock_session_scope.return_value.__enter__.return_value = session
        mock_session_scope.return_value.__exit__.return_value = False

        reset_count = reset_stuck_filing_extractions()
        self.assertEqual(1, reset_count)

        row = session.get(FilingDocument, 1)
        assert row is not None
        self.assertEqual(FilingDocument.STATUS_PENDING, row.analysis_status)

    @patch('compute.filing_store.session_scope')
    def test_count_extractable_filings(self, mock_session_scope):
        self._add_filing('000001', FilingDocument.STATUS_PENDING)
        self._add_filing('000002', FilingDocument.STATUS_FAILED)
        self._add_filing('000003', FilingDocument.STATUS_PROCESSING)
        self._add_filing('000004', FilingDocument.STATUS_EXTRACTED)

        session = self.session_factory()
        mock_session_scope.return_value.__enter__.return_value = session
        mock_session_scope.return_value.__exit__.return_value = False

        counts = count_extractable_filings()
        self.assertEqual(1, counts[FilingDocument.STATUS_PENDING])
        self.assertEqual(1, counts[FilingDocument.STATUS_FAILED])
        self.assertEqual(1, counts[FilingDocument.STATUS_PROCESSING])
        self.assertEqual(3, counts['total'])


class FilingPipelineStepsTestCase(unittest.TestCase):
    def test_skip_sync_step_when_env_set(self):
        from jobs.filing_pipeline import build_filing_pipeline_steps

        with patch.dict(os.environ, {'TW_FILING_SKIP_SYNC': '1'}, clear=False):
            steps = build_filing_pipeline_steps({})
        self.assertEqual(['filing_extract'], [name for name, _ in steps])

    def test_resume_enables_extract_until_done_by_default(self):
        from jobs.filing_pipeline import _filing_env

        with patch.dict(os.environ, {'TW_FILING_RESUME': '1'}, clear=False):
            env = _filing_env()
        self.assertTrue(env['resume'])
        self.assertTrue(env['extract_until_done'])


if __name__ == '__main__':
    unittest.main()

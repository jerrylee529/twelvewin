# -*- coding: utf-8 -*-

import datetime
import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.db.models import Base, FilingAiAnalysis, FilingDocument, FilingTextChunk
from api.services.filings import (
    get_filing_analysis,
    get_filing_content,
    list_filings,
    upsert_filing_analysis,
)


class FilingServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        now = datetime.datetime.now()
        self.filing = FilingDocument(
            code='000001',
            year=2024,
            season=0,
            report_kind='annual',
            report_type_label='年报',
            qiniu_key='000001_年报_2024_20250315.pdf',
            filename='000001_年报_2024_20250315.pdf',
            publish_date=datetime.date(2025, 3, 15),
            analysis_status=FilingDocument.STATUS_EXTRACTED,
            synced_at=now,
            extracted_at=now,
            page_count=2,
        )
        self.session.add(self.filing)
        self.session.flush()
        self.session.add(
            FilingTextChunk(
                filing_id=self.filing.id,
                page_no=1,
                section='management_discussion',
                chunk_index=0,
                content='管理层讨论：净利润同比增长 10%。',
                token_count=20,
            )
        )
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_list_filings(self):
        result = list_filings(self.session, '000001')
        self.assertEqual(1, result.total)
        self.assertEqual('2024 年报', result.rows[0]['display_label'])

    def test_get_filing_content(self):
        payload = get_filing_content(self.session, '000001', 2024, 0)
        self.assertNotIn('error', payload)
        self.assertIn('analysis_text', payload)
        self.assertIn('净利润', payload['analysis_text'])

    def test_upsert_filing_analysis(self):
        saved = upsert_filing_analysis(
            self.session,
            '000001',
            2024,
            0,
            {
                'summary': '2024 年报业绩稳健',
                'highlights': [{'title': '盈利', 'detail': '净利润增长', 'page': 1}],
                'risks': [{'level': '中', 'title': '行业竞争'}],
                'full_markdown': '详细解读',
            },
        )
        self.assertEqual('2024 年报业绩稳健', saved['summary'])
        self.assertEqual(FilingDocument.STATUS_DONE, self.session.get(FilingDocument, self.filing.id).analysis_status)

        cached = get_filing_analysis(self.session, '000001', 2024, 0)
        self.assertIsNotNone(cached)
        assert cached is not None
        self.assertEqual('盈利', cached['highlights'][0]['title'])


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-

"""Parse Qiniu OSS filing PDF filenames into structured metadata."""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass

# {code}_{report_type}_{report_year}_{publish_date}.pdf
# Example: 000001_年报_2024_20250315.pdf
FILING_FILENAME_RE = re.compile(
    r'^(\d{6})_(.+?)_(\d{4})_(\d{8})\.pdf$',
    re.IGNORECASE,
)

REPORT_TYPE_LABELS: dict[str, tuple[str, int]] = {
    '年报': ('annual', 0),
    '半年报': ('semi_annual', 2),
    '第一季度季报': ('quarterly', 1),
    '第二季度季报': ('quarterly', 2),
    '第三季度季报': ('quarterly', 3),
    '第四季度季报': ('quarterly', 4),
}

SEASON_LABELS: dict[int, str] = {
    0: '年报',
    1: '第一季度季报',
    2: '半年报',
    3: '第三季度季报',
    4: '第四季度季报',
}


@dataclass(frozen=True)
class ParsedFilingName:
    code: str
    report_type_label: str
    report_kind: str
    year: int
    season: int
    publish_date: datetime.date
    filename: str

    @property
    def display_label(self) -> str:
        if self.season == 0:
            return f'{self.year} 年报'
        if self.season == 2 and self.report_kind == 'semi_annual':
            return f'{self.year} 半年报'
        season_label = SEASON_LABELS.get(self.season, self.report_type_label)
        return f'{self.year} {season_label}'


def parse_filing_filename(name: str) -> ParsedFilingName | None:
    """Parse a Qiniu object key or bare filename into filing metadata."""
    basename = name.rsplit('/', 1)[-1].strip()
    match = FILING_FILENAME_RE.match(basename)
    if not match:
        return None

    code, type_label, year_raw, publish_raw = match.groups()
    mapping = REPORT_TYPE_LABELS.get(type_label.strip())
    if mapping is None:
        return None

    report_kind, season = mapping
    try:
        publish_date = datetime.datetime.strptime(publish_raw, '%Y%m%d').date()
        year = int(year_raw)
    except ValueError:
        return None

    return ParsedFilingName(
        code=code,
        report_type_label=type_label.strip(),
        report_kind=report_kind,
        year=year,
        season=season,
        publish_date=publish_date,
        filename=basename,
    )


def filing_object_key(code: str, parsed: ParsedFilingName, *, prefix: str = '') -> str:
    """Rebuild the expected object key for a parsed filing."""
    normalized_prefix = prefix.strip('/')
    if normalized_prefix:
        return f'{normalized_prefix}/{parsed.filename}'
    return parsed.filename

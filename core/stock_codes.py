# -*- coding: utf-8 -*-

"""Helpers for preserving A-share stock code text."""

import re


def normalize_stock_code(value):
    """Return stock codes as display-safe strings without losing leading zeros."""
    if value is None:
        return ''

    text = str(value).strip()
    if not text or text.lower() in ('nan', 'none', 'nat'):
        return ''

    numeric_match = re.match(r'^(\d+)(?:\.0+)?$', text)
    if numeric_match:
        digits = numeric_match.group(1)
        if len(digits) < 6:
            return digits.zfill(6)
        return digits

    return text

# -*- coding: utf-8 -*-

"""Qiniu Cloud OSS helpers for filing PDF objects."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterator

from core.filing_names import parse_filing_filename


@dataclass(frozen=True)
class QiniuObjectInfo:
    key: str
    size: int | None
    hash_value: str | None


class QiniuConfigError(RuntimeError):
    pass


def _require_qiniu_sdk():
    try:
        from qiniu import Auth, BucketManager
    except ImportError as exc:
        raise QiniuConfigError(
            'qiniu package is required for filing sync. Install requirements-analysis.txt.'
        ) from exc
    return Auth, BucketManager


def load_qiniu_settings() -> dict[str, str | int]:
    access_key = os.environ.get('QINIU_ACCESS_KEY', '').strip()
    secret_key = os.environ.get('QINIU_SECRET_KEY', '').strip()
    bucket = os.environ.get('QINIU_BUCKET', '').strip()
    domain = os.environ.get('QINIU_DOMAIN', '').strip()
    prefix = os.environ.get('QINIU_FILING_PREFIX', '').strip().strip('/')
    ttl = int(os.environ.get('QINIU_SIGNED_URL_TTL', '900') or '900')

    if not all([access_key, secret_key, bucket]):
        raise QiniuConfigError(
            'QINIU_ACCESS_KEY, QINIU_SECRET_KEY, and QINIU_BUCKET must be set.'
        )

    return {
        'access_key': access_key,
        'secret_key': secret_key,
        'bucket': bucket,
        'domain': domain,
        'prefix': prefix,
        'ttl': ttl,
    }


def build_list_prefix(code: str | None = None) -> str:
    settings = load_qiniu_settings()
    prefix = settings['prefix']
    if code:
        code_prefix = f'{code}_'
        if prefix:
            return f'{prefix}/{code_prefix}'
        return code_prefix
    if prefix:
        return f'{prefix}/'
    return ''


def iter_filing_objects(code: str | None = None, *, limit: int = 0) -> Iterator[QiniuObjectInfo]:
    Auth, BucketManager = _require_qiniu_sdk()
    settings = load_qiniu_settings()
    auth = Auth(settings['access_key'], settings['secret_key'])
    manager = BucketManager(auth)
    prefix = build_list_prefix(code)
    marker = None
    fetched = 0

    while True:
        ret, eof, info = manager.list(
            settings['bucket'],
            prefix=prefix,
            marker=marker,
            limit=1000,
        )
        if info.status_code != 200:
            raise RuntimeError(f'Qiniu list failed: status={info.status_code}')

        for item in ret.get('items', []):
            key = item.get('key', '')
            if not key.lower().endswith('.pdf'):
                continue
            if parse_filing_filename(key) is None:
                continue
            yield QiniuObjectInfo(
                key=key,
                size=item.get('fsize'),
                hash_value=item.get('hash'),
            )
            fetched += 1
            if limit > 0 and fetched >= limit:
                return

        if eof:
            break
        marker = ret.get('marker')


def download_filing_bytes(key: str) -> bytes:
    Auth, BucketManager = _require_qiniu_sdk()
    settings = load_qiniu_settings()
    auth = Auth(settings['access_key'], settings['secret_key'])
    domain = settings['domain']
    if not domain:
        raise QiniuConfigError('QINIU_DOMAIN is required to download filing PDFs.')

    base_url = domain if domain.startswith('http') else f'https://{domain}'
    private_url = auth.private_download_url(f'{base_url.rstrip("/")}/{key.lstrip("/")}', expires=3600)

    import urllib.request

    with urllib.request.urlopen(private_url, timeout=120) as response:
        return response.read()


def signed_filing_url(key: str, *, ttl: int | None = None) -> str:
    Auth, _BucketManager = _require_qiniu_sdk()
    settings = load_qiniu_settings()
    auth = Auth(settings['access_key'], settings['secret_key'])
    domain = settings['domain']
    if not domain:
        raise QiniuConfigError('QINIU_DOMAIN is required for signed filing URLs.')

    expires = ttl if ttl is not None else int(settings['ttl'])
    base_url = domain if domain.startswith('http') else f'https://{domain}'
    return auth.private_download_url(
        f'{base_url.rstrip("/")}/{key.lstrip("/")}',
        expires=expires,
    )

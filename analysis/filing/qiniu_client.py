# -*- coding: utf-8 -*-

"""Qiniu Cloud OSS helpers for filing PDF objects."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterator

from urllib.parse import quote

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


def _parse_list_items(items) -> list[QiniuObjectInfo]:
    objects: list[QiniuObjectInfo] = []
    for item in items:
        key = item.get('key', '')
        if not key.lower().endswith('.pdf'):
            continue
        if parse_filing_filename(key) is None:
            continue
        objects.append(
            QiniuObjectInfo(
                key=key,
                size=item.get('fsize'),
                hash_value=item.get('hash'),
            )
        )
    return objects


def list_filing_objects_page(
    code: str | None = None,
    *,
    marker: str | None = None,
    page_size: int = 1000,
) -> tuple[list[QiniuObjectInfo], str | None, bool]:
    """List one Qiniu page and return ``(objects, next_marker, eof)``."""
    Auth, BucketManager = _require_qiniu_sdk()
    settings = load_qiniu_settings()
    auth = Auth(settings['access_key'], settings['secret_key'])
    manager = BucketManager(auth)
    prefix = build_list_prefix(code)
    ret, eof, info = manager.list(
        settings['bucket'],
        prefix=prefix,
        marker=marker,
        limit=page_size,
    )
    if info.status_code != 200:
        raise RuntimeError(f'Qiniu list failed: status={info.status_code}')

    next_marker = None if eof else ret.get('marker')
    return _parse_list_items(ret.get('items', [])), next_marker, eof


def iter_filing_objects(
    code: str | None = None,
    *,
    limit: int = 0,
    marker: str | None = None,
) -> Iterator[QiniuObjectInfo]:
    fetched = 0
    page_marker = marker

    while True:
        objects, next_marker, eof = list_filing_objects_page(code, marker=page_marker)
        for obj in objects:
            yield obj
            fetched += 1
            if limit > 0 and fetched >= limit:
                return

        if eof:
            break
        page_marker = next_marker


def _object_resource_url(base_url: str, key: str) -> str:
    """Build a download URL with an ASCII-safe, percent-encoded object key."""
    encoded_key = quote(key.lstrip('/'), safe='/')
    return f'{base_url.rstrip("/")}/{encoded_key}'


def _is_s3_domain(domain: str) -> bool:
    return 'qiniucs.com' in domain.lower()


def _s3_region_from_domain(domain: str) -> str:
    host = domain.split('://', 1)[-1].split('/', 1)[0]
    parts = host.split('.')
    for index, part in enumerate(parts):
        if part == 's3' and index + 1 < len(parts):
            return parts[index + 1]
    return os.environ.get('QINIU_S3_REGION', 'cn-south-1').strip() or 'cn-south-1'


def _s3_endpoint_url(domain: str) -> str:
    explicit = os.environ.get('QINIU_S3_ENDPOINT', '').strip()
    if explicit:
        return explicit.rstrip('/')
    region = _s3_region_from_domain(domain)
    return f'https://s3.{region}.qiniucs.com'


def _download_via_s3_api(key: str) -> bytes:
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:
        raise QiniuConfigError(
            'boto3 is required for Qiniu S3-compatible domains. Install requirements-analysis.txt.'
        ) from exc

    settings = load_qiniu_settings()
    domain = settings['domain']
    if not domain:
        raise QiniuConfigError('QINIU_DOMAIN is required to download filing PDFs.')

    client = boto3.client(
        's3',
        endpoint_url=_s3_endpoint_url(domain),
        aws_access_key_id=str(settings['access_key']),
        aws_secret_access_key=str(settings['secret_key']),
        region_name=_s3_region_from_domain(domain),
        config=Config(signature_version='s3v4'),
    )
    response = client.get_object(Bucket=str(settings['bucket']), Key=key.lstrip('/'))
    return response['Body'].read()


def _private_download_url(auth, base_url: str, key: str, *, expires: int) -> str:
    # Qiniu signs the exact URL string; encode the key before signing.
    return auth.private_download_url(_object_resource_url(base_url, key), expires=expires)


def download_filing_bytes(key: str) -> bytes:
    settings = load_qiniu_settings()
    domain = settings['domain']
    if not domain:
        raise QiniuConfigError('QINIU_DOMAIN is required to download filing PDFs.')

    if _is_s3_domain(domain):
        return _download_via_s3_api(key)

    Auth, _BucketManager = _require_qiniu_sdk()
    auth = Auth(settings['access_key'], settings['secret_key'])
    base_url = domain if domain.startswith('http') else f'https://{domain}'
    private_url = _private_download_url(auth, base_url, key, expires=3600)

    import urllib.request

    with urllib.request.urlopen(private_url, timeout=120) as response:
        return response.read()


def signed_filing_url(key: str, *, ttl: int | None = None) -> str:
    settings = load_qiniu_settings()
    domain = settings['domain']
    if not domain:
        raise QiniuConfigError('QINIU_DOMAIN is required for signed filing URLs.')

    if _is_s3_domain(domain):
        raise QiniuConfigError(
            'Signed filing URLs are not supported for Qiniu S3-compatible domains. '
            'Bind a Kodo CDN domain to QINIU_DOMAIN or download via compute jobs only.'
        )

    Auth, _BucketManager = _require_qiniu_sdk()
    auth = Auth(settings['access_key'], settings['secret_key'])
    expires = ttl if ttl is not None else int(settings['ttl'])
    base_url = domain if domain.startswith('http') else f'https://{domain}'
    return _private_download_url(auth, base_url, key, expires=expires)

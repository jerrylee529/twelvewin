# -*- coding: utf-8 -*-

"""Read precomputed industry clusters from stock_cluster tables."""

from app import db
from app.models import Instrument, StockCluster, StockClusterItem


def _median(values):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    half = len(ordered) // 2
    return (ordered[half] + ordered[~half]) / 2


def get_industry_cluster_payload(industry: str) -> dict:
    """
    Build the JSON payload for /industry/data from DB-backed cluster results.
    """
    if not industry:
        return {'total': 0, 'rows': []}

    instruments = (
        db.session.query(Instrument)
        .filter(Instrument.industry == industry)
        .all()
    )
    if not instruments:
        return {'total': 0, 'rows': []}

    centers = (
        db.session.query(StockCluster)
        .filter(StockCluster.section == industry)
        .all()
    )
    center_labels = {center.code: index for index, center in enumerate(centers)}

    items = (
        db.session.query(StockClusterItem)
        .filter(StockClusterItem.section == industry)
        .all()
    )
    code_to_label = {}
    for item in items:
        code_to_label[item.code] = center_labels.get(item.parent_code, 0)

    rows = []
    pe_list = []
    pb_list = []
    esp_list = []
    bvps_list = []
    gpr_list = []
    npr_list = []

    for index, instrument in enumerate(instruments, start=1):
        label = code_to_label.get(instrument.code, 0)
        row = {
            'id': index,
            'label': label + 1,
            'industry': instrument.industry,
            'code': instrument.code,
            'name': instrument.name,
            'pe': instrument.pe,
            'outstanding': instrument.outstanding,
            'totals': instrument.totals,
            'total_assets': instrument.total_assets,
            'liquid_assets': instrument.liquid_assets,
            'fixed_assets': instrument.fixed_assets,
            'esp': round(instrument.esp or 0, 2),
            'bvps': instrument.bvps,
            'pb': instrument.pb,
            'time_2_market': instrument.time_2_market,
            'gpr': instrument.gpr,
            'npr': instrument.npr,
            'holders': instrument.holders,
        }
        rows.append(row)

        if instrument.pe is not None:
            pe_list.append(instrument.pe)
        if instrument.pb is not None:
            pb_list.append(instrument.pb)
        if instrument.esp is not None:
            esp_list.append(instrument.esp)
        if instrument.bvps is not None:
            bvps_list.append(instrument.bvps)
        if instrument.gpr is not None:
            gpr_list.append(instrument.gpr)
        if instrument.npr is not None:
            npr_list.append(instrument.npr)

    rows.sort(key=lambda item: item['label'])

    result = {'total': len(rows), 'rows': rows}
    if rows:
        count = len(rows)
        result['avg_pe'] = round(sum(pe_list) / len(pe_list), 2) if pe_list else 0
        result['avg_pb'] = round(sum(pb_list) / len(pb_list), 2) if pb_list else 0
        result['avg_esp'] = round(sum(esp_list) / len(esp_list), 2) if esp_list else 0
        result['avg_bvps'] = round(sum(bvps_list) / len(bvps_list), 2) if bvps_list else 0
        result['avg_gpr'] = round(sum(gpr_list) / len(gpr_list), 2) if gpr_list else 0
        result['avg_npr'] = round(sum(npr_list) / len(npr_list), 2) if npr_list else 0
        result['mid_pe'] = round(_median(pe_list), 2)
        result['mid_pb'] = round(_median(pb_list), 2)
        result['mid_esp'] = round(_median(esp_list), 2)
        result['mid_bvps'] = round(_median(bvps_list), 2)
        result['mid_gpr'] = round(_median(gpr_list), 2)
        result['mid_npr'] = round(_median(npr_list), 2)

    return result


def get_industry_stock_payload(industry: str, code: str) -> dict:
    """Rows in the same cluster as ``code`` within ``industry``."""
    payload = get_industry_cluster_payload(industry)
    rows = payload.get('rows') or []
    target = next((row for row in rows if row['code'] == code), None)
    if target is None:
        return {'total': 0, 'rows': []}

    label = target['label']
    cluster_rows = [row for row in rows if row['label'] == label]
    result = {
        'total': len(cluster_rows),
        'rows': cluster_rows,
    }
    if cluster_rows:
        for key in ('avg_pe', 'avg_pb', 'avg_esp', 'avg_bvps', 'avg_gpr', 'avg_npr',
                    'mid_pe', 'mid_pb', 'mid_esp', 'mid_bvps', 'mid_gpr', 'mid_npr'):
            if key in payload:
                result[key] = payload[key]
    return result

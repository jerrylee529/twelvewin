# -*- coding: utf-8 -*-

"""Cluster results for index sections and industries."""

from sqlalchemy.orm import Session

from api.db.models import StockCluster, StockClusterItem
from api.services.types import QueryResult


def get_cluster_payload(session: Session, section: str) -> QueryResult:
    if not section or section == 'all':
        return QueryResult()

    clusters = session.query(StockCluster).filter_by(section=section).all()
    cluster_items = session.query(StockClusterItem).filter_by(section=section).all()

    rows = []
    for index, cluster in enumerate(clusters, start=1):
        items = [
            {
                'code': cluster.code,
                'name': cluster.name,
                'corr': 1.0,
            }
        ]
        for cluster_item in cluster_items:
            if cluster.code == cluster_item.parent_code:
                items.append(
                    {
                        'code': cluster_item.code,
                        'name': cluster_item.name,
                        'corr': cluster_item.corr,
                    }
                )

        rows.append(
            {
                'id': index,
                'code': cluster.code,
                'name': cluster.name,
                'items': items,
            }
        )

    return QueryResult(rows=rows)

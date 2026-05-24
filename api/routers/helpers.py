# -*- coding: utf-8 -*-

from api.schemas.responses import TableResponse
from api.services.types import QueryResult


def to_table_response(result: QueryResult) -> TableResponse:
    return TableResponse(
        total=result.total,
        rows=result.rows,
        updateTime=result.update_time,
        error=result.error,
    )

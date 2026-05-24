# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class QueryResult:
    rows: list[dict[str, Any]] = field(default_factory=list)
    update_time: Optional[str] = None
    error: Optional[str] = None
    total_count: Optional[int] = None

    @property
    def total(self) -> int:
        if self.total_count is not None:
            return self.total_count
        return len(self.rows)

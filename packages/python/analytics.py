from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from packages.python.storage import list_validations
from packages.python.lifecycle_analytics import trade_lifecycle_summary


def strategy_performance_summary(limit: int = 500) -> list[dict[str, Any]]:
    rows = list_validations(limit=limit)
    bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        bucket[row["strategy"]].append(row)

    result: list[dict[str, Any]] = []
    for strategy, items in bucket.items():
        result.append(
            {
                "strategy": strategy,
                "count": len(items),
                "avg_return_1d": round(mean((x["return_1d"] or 0) for x in items), 2),
                "avg_return_3d": round(mean((x["return_3d"] or 0) for x in items), 2),
                "avg_return_5d": round(mean((x["return_5d"] or 0) for x in items), 2),
                "win_rate_1d": round(
                    sum(1 for x in items if (x["return_1d"] or 0) > 0) / max(len(items), 1) * 100,
                    2,
                ),
            }
        )
    return sorted(result, key=lambda x: (x["avg_return_1d"], x["win_rate_1d"]), reverse=True)

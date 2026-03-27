from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from packages.python.storage import list_paper_trade_attribution


def trade_lifecycle_summary(limit: int = 200) -> dict[str, Any]:
    rows = list_paper_trade_attribution(limit=limit)
    by_reason: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_action: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_state: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        by_reason[str(row.get('reason') or 'unknown')].append(row)
        by_action[str(row.get('action') or 'unknown')].append(row)
        by_state[str(row.get('lifecycle_state') or 'unknown')].append(row)

    def summarize(bucket: dict[str, list[dict[str, Any]]], key_name: str) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for key, items in bucket.items():
            returns = [float(x['return_pct']) for x in items if x.get('return_pct') is not None]
            peaks = [float(x['peak_return_pct']) for x in items if x.get('peak_return_pct') is not None]
            result.append({
                key_name: key,
                'count': len(items),
                'avg_return_pct': round(mean(returns), 2) if returns else None,
                'avg_peak_return_pct': round(mean(peaks), 2) if peaks else None,
                'win_rate_pct': round(sum(1 for x in returns if x > 0) / len(returns) * 100, 2) if returns else None,
            })
        return sorted(result, key=lambda x: ((x.get('avg_return_pct') if x.get('avg_return_pct') is not None else -999), x['count']), reverse=True)

    return {
        'count': len(rows),
        'by_reason': summarize(by_reason, 'reason'),
        'by_action': summarize(by_action, 'action'),
        'by_state': summarize(by_state, 'lifecycle_state'),
        'recent': rows[:20],
    }

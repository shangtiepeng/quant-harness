from __future__ import annotations

from collections import defaultdict
from typing import Any


def aggregate_signal_candidates(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in signals:
        bucket[signal['symbol']].append(signal)

    result: list[dict[str, Any]] = []
    for symbol, items in bucket.items():
        ranked = sorted(items, key=lambda x: (x.get('resonance_score', 0), x.get('score', 0)), reverse=True)
        best = ranked[0]
        strategies = sorted({str(item.get('strategy', '')) for item in items if item.get('strategy')})
        reasons: list[str] = []
        seen: set[str] = set()
        for item in ranked:
            for reason in (item.get('resonance_reasons') or [])[:4]:
                if reason in seen:
                    continue
                seen.add(reason)
                reasons.append(reason)
        result.append(
            {
                'symbol': symbol,
                'name': best['name'],
                'display': f"{best['name']} ({symbol})",
                'theme': best.get('theme', ''),
                'secondary_theme': best.get('secondary_theme', ''),
                'concepts': best.get('concepts', []),
                'risk_level': best.get('risk_level', 'medium'),
                'resonance_score': round(max(item.get('resonance_score', 0) for item in items), 1),
                'resonance_level': best.get('resonance_level', 'D'),
                'resonance_role': best.get('resonance_role', 'noise'),
                'strategy_count': len(strategies),
                'strategies': strategies,
                'strategy_labels': strategies,
                'source_signals': ranked,
                'resonance_reasons': reasons[:6],
                'score': best.get('score', 0),
            }
        )

    return sorted(
        result,
        key=lambda x: (x['resonance_score'], x['strategy_count'], x['score']),
        reverse=True,
    )

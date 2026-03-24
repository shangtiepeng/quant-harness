from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from packages.python.storage import list_validation_signal_details


LEVEL_ORDER = ['A', 'B', 'C', 'D']
STAGE_ORDER = ['ice', 'repair', 'split', 'hot']


def _summary(items: list[dict[str, Any]], label: str) -> dict[str, Any]:
    return {
        'bucket': label,
        'count': len(items),
        'avg_return_1d': round(mean((x.get('return_1d') or 0) for x in items), 2) if items else 0,
        'avg_return_3d': round(mean((x.get('return_3d') or 0) for x in items), 2) if items else 0,
        'avg_return_5d': round(mean((x.get('return_5d') or 0) for x in items), 2) if items else 0,
        'win_rate_1d': round(sum(1 for x in items if (x.get('return_1d') or 0) > 0) / max(len(items), 1) * 100, 2),
    }


def resonance_validation_summary(limit: int = 500) -> dict[str, Any]:
    rows = list_validation_signal_details(limit=limit)

    by_level: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_mainline: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_stage: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_consensus: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        signal = row.get('signal') or {}
        market = row.get('market') or {}
        level = str(signal.get('resonance_level', 'D'))
        role = str(signal.get('resonance_role', 'noise'))
        stage = str(market.get('market_sentiment_stage', 'unknown'))
        is_mainline = role in {'mainline_leader', 'frontline_core'}
        consensus = 'double_strategy' if signal.get('strategy') in {'leader', 'hotmoney'} and (signal.get('resonance_score') or 0) >= 65 else 'single_strategy'

        enriched = {
            **row,
            'resonance_level': level,
            'resonance_role': role,
            'market_stage': stage,
            'is_mainline': is_mainline,
            'consensus_bucket': consensus,
        }
        by_level[level].append(enriched)
        by_mainline['mainline' if is_mainline else 'non_mainline'].append(enriched)
        by_stage[stage].append(enriched)
        by_consensus[consensus].append(enriched)

    return {
        'by_resonance_level': [_summary(by_level[level], level) for level in LEVEL_ORDER if by_level.get(level)],
        'by_mainline': [_summary(by_mainline[key], key) for key in ['mainline', 'non_mainline'] if by_mainline.get(key)],
        'by_market_stage': [_summary(by_stage[key], key) for key in STAGE_ORDER if by_stage.get(key)],
        'by_consensus': [_summary(by_consensus[key], key) for key in ['double_strategy', 'single_strategy'] if by_consensus.get(key)],
        'sample_size': len(rows),
    }

from __future__ import annotations

from typing import Any


STRATEGY_LABELS = {
    'leader': '龙头策略',
    'hotmoney': '游资共振策略',
    'sentiment': '情绪策略',
    'composite': '综合策略',
}


def build_portfolio_plan(market: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    stage = market.get('market_sentiment_stage', 'ice')

    if stage == 'ice':
        risk_mode = 'defensive_probe'
        risk_budget = 20
        enabled_strategies = ['leader', 'hotmoney']
        notes = [
            '情绪冰点，以轻仓试错为主。',
            '优先保留高共振候选，不做弱共振扩散交易。',
        ]
    elif stage == 'repair':
        risk_mode = 'selective_attack'
        risk_budget = 45
        enabled_strategies = ['leader', 'hotmoney', 'sentiment']
        notes = [
            '情绪修复阶段，允许适度提高仓位。',
            '优先主线前排与强共振候选。',
        ]
    elif stage == 'hot':
        risk_mode = 'active_attack'
        risk_budget = 60
        enabled_strategies = ['leader', 'hotmoney', 'sentiment', 'composite']
        notes = [
            '情绪高潮阶段，允许主动进攻，但要提防次日一致性崩塌。',
            '避免后排补涨过度扩散。',
        ]
    else:
        risk_mode = 'risk_control'
        risk_budget = 30
        enabled_strategies = ['leader', 'hotmoney']
        notes = [
            '分歧阶段优先保留核心，降低总暴露。',
            '回避纯跟风和低共振标的。',
        ]

    ranked = []
    for item in candidates:
        strategy_overlap = len(item.get('strategies') or [])
        resonance_score = float(item.get('resonance_score') or 0)
        alloc_score = resonance_score + strategy_overlap * 6
        ranked.append({
            **item,
            'allocation_score': round(alloc_score, 1),
        })
    ranked = sorted(ranked, key=lambda x: x['allocation_score'], reverse=True)

    plan_items: list[dict[str, Any]] = []
    remaining_budget = risk_budget
    max_positions = 3 if risk_budget <= 30 else 4
    per_position_cap = 10 if risk_budget <= 20 else 15 if risk_budget <= 45 else 20

    for item in ranked[:max_positions]:
        if remaining_budget <= 0:
            break
        level = item.get('resonance_level', 'D')
        if level == 'D':
            continue
        suggested = per_position_cap
        if level == 'B':
            suggested = min(suggested, 12 if risk_budget <= 45 else 16)
        elif level == 'C':
            suggested = min(suggested, 8)
        if len(item.get('strategies') or []) >= 2:
            suggested += 2
        suggested = min(suggested, remaining_budget)
        remaining_budget -= suggested
        plan_items.append({
            'symbol': item['symbol'],
            'name': item['name'],
            'display': item['display'],
            'theme': item.get('theme', ''),
            'resonance_level': item.get('resonance_level', 'D'),
            'resonance_score': item.get('resonance_score', 0),
            'strategies': item.get('strategies', []),
            'target_weight_pct': suggested,
            'role': item.get('resonance_role', 'noise'),
            'thesis': ' / '.join(item.get('resonance_reasons', [])[:3]),
        })

    no_trade = len(plan_items) == 0 or risk_budget == 0

    strategy_weights = []
    if enabled_strategies:
        base = 100 / len(enabled_strategies)
        for strategy in enabled_strategies:
            adjust = 10 if strategy == 'leader' and stage in {'repair', 'hot'} else 0
            strategy_weights.append({
                'strategy': strategy,
                'label': STRATEGY_LABELS.get(strategy, strategy),
                'weight_pct': round(base + adjust, 1),
            })
        total = sum(item['weight_pct'] for item in strategy_weights) or 1
        for item in strategy_weights:
            item['weight_pct'] = round(item['weight_pct'] / total * 100, 1)

    return {
        'market_stage': stage,
        'risk_mode': risk_mode,
        'risk_budget_pct': risk_budget,
        'enabled_strategies': enabled_strategies,
        'strategy_weights': strategy_weights,
        'candidate_plan': plan_items,
        'no_trade': no_trade,
        'notes': notes,
    }

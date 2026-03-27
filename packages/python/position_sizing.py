from __future__ import annotations

from collections import defaultdict
from typing import Any


MIN_POSITION_PCT = 3.0


def apply_position_sizing(portfolio_plan: dict[str, Any], risk_profile: dict[str, Any]) -> dict[str, Any]:
    items = [dict(item) for item in (portfolio_plan.get('candidate_plan') or [])]
    limits = dict(risk_profile.get('limits') or {})
    risk_discount = float(risk_profile.get('risk_discount') or 1.0)
    cooldown = bool(risk_profile.get('cooldown'))
    diagnostics = {
        item['symbol']: item for item in (risk_profile.get('candidate_diagnostics') or [])
    }

    single_position_cap = float(limits.get('single_position_cap_pct') or portfolio_plan.get('per_position_cap_pct') or 10)
    single_theme_cap = float(limits.get('single_theme_cap_pct') or portfolio_plan.get('max_theme_exposure_pct') or 15)
    single_strategy_cap = float(limits.get('single_strategy_cap_pct') or 20)
    daily_new_exposure_cap = float(limits.get('daily_new_exposure_cap_pct') or portfolio_plan.get('risk_budget_pct') or 20)

    adjusted_budget = round(min(float(portfolio_plan.get('risk_budget_pct') or 0), daily_new_exposure_cap) * risk_discount, 1)
    if cooldown:
        adjusted_budget = min(adjusted_budget, single_position_cap)

    theme_exposure: dict[str, float] = defaultdict(float)
    strategy_exposure: dict[str, float] = defaultdict(float)
    planned: list[dict[str, Any]] = []
    remaining_budget = adjusted_budget
    notes = list(portfolio_plan.get('notes') or [])
    dropped: list[dict[str, Any]] = []

    ranked = sorted(
        items,
        key=lambda item: (
            diagnostics.get(item['symbol'], {}).get('quality_multiplier', 1.0),
            float(item.get('resonance_score') or 0),
            len(item.get('strategies') or []),
        ),
        reverse=True,
    )

    for item in ranked:
        if remaining_budget < MIN_POSITION_PCT:
            dropped.append({'symbol': item['symbol'], 'reason': 'budget_exhausted'})
            continue
        diag = diagnostics.get(item['symbol'], {})
        base_weight = float(item.get('target_weight_pct') or 0)
        quality_multiplier = float(diag.get('quality_multiplier') or 1.0)
        suggested = round(base_weight * quality_multiplier * risk_discount, 1)
        if item.get('resonance_level') == 'A':
            suggested += 1.0
        elif item.get('resonance_level') == 'C':
            suggested -= 1.0

        theme = str(item.get('theme') or '未分类')
        strategies = item.get('strategies') or []
        allowed_by_theme = single_theme_cap - theme_exposure[theme]
        allowed_by_strategy = min(
            [single_strategy_cap - strategy_exposure[strategy] for strategy in strategies] or [single_strategy_cap]
        )
        allowed = min(single_position_cap, remaining_budget, allowed_by_theme, allowed_by_strategy)
        target_weight = round(min(max(MIN_POSITION_PCT, suggested), allowed), 1)
        if target_weight < MIN_POSITION_PCT or allowed < MIN_POSITION_PCT:
            dropped.append({'symbol': item['symbol'], 'reason': 'risk_limit_blocked'})
            continue

        item['target_weight_pct'] = target_weight
        item['sizing_meta'] = {
            'base_weight_pct': base_weight,
            'quality_multiplier': quality_multiplier,
            'risk_discount': risk_discount,
            'allowed_cap_pct': round(allowed, 1),
        }
        planned.append(item)
        remaining_budget = round(remaining_budget - target_weight, 1)
        theme_exposure[theme] += target_weight
        for strategy in strategies:
            strategy_exposure[strategy] += target_weight

        if cooldown:
            break

    no_trade = len(planned) == 0
    if cooldown:
        notes.append('冷静模式启用：仅保留 1 笔最高质量候选。')
    if remaining_budget > 0:
        notes.append(f'剩余未使用风险预算 {remaining_budget}% 。')
    if no_trade:
        notes.append('仓位引擎未放行任何新仓。')

    return {
        **portfolio_plan,
        'candidate_plan': planned,
        'risk_budget_pct': adjusted_budget,
        'per_position_cap_pct': single_position_cap,
        'max_theme_exposure_pct': single_theme_cap,
        'max_strategy_exposure_pct': single_strategy_cap,
        'theme_exposure': {k: round(v, 1) for k, v in theme_exposure.items()},
        'strategy_exposure': {k: round(v, 1) for k, v in strategy_exposure.items()},
        'remaining_risk_budget_pct': remaining_budget,
        'dropped_candidates': dropped,
        'no_trade': no_trade,
        'notes': notes,
    }

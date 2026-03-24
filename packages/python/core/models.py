from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class StockSnapshot(BaseModel):
    symbol: str
    name: str
    theme: str
    secondary_theme: str = ""
    concepts: list[str] = []
    close: float
    pct_change: float
    volume_ratio: float
    turnover_rate: float
    board_height: int = 0
    is_limit_up: bool = False
    is_broken_board: bool = False
    hot_money_net_buy_million: float = 0.0
    auction_strength: float = 0.0
    seal_strength: float = 0.0
    narrative_score: float = 0.0


class StrategySignal(BaseModel):
    strategy: Literal["leader", "sentiment", "hotmoney", "composite"]
    symbol: str
    name: str
    score: float = Field(ge=0, le=100)
    risk_level: Literal["low", "medium", "high"]
    reasons: list[str]
    entry_note: str
    exit_note: str
    invalidation_note: str
    theme: str
    secondary_theme: str = ""
    concepts: list[str] = []
    resonance_score: float = Field(default=0, ge=0, le=100)
    resonance_level: Literal["A", "B", "C", "D"] = "D"
    resonance_role: str = "noise"
    resonance_reasons: list[str] = []


class MarketOverview(BaseModel):
    trade_date: str
    market_sentiment_stage: Literal["ice", "repair", "split", "hot"]
    limit_up_count: int
    limit_down_count: int
    broken_board_rate: float
    highest_board: int
    notes: list[str]


class DailyReport(BaseModel):
    trade_date: str
    market: MarketOverview
    top_signals: list[StrategySignal]
    summary_cn: str
    summary_en: str

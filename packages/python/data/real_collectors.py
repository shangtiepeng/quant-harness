from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from packages.python.core.models import StockSnapshot
from packages.python.data.sample_loader import load_sample_market


def _normalize_records(records: list[dict[str, Any]]) -> list[StockSnapshot]:
    result: list[StockSnapshot] = []
    for item in records:
        pct = float(item.get("涨跌幅", item.get("pct_change", 0)) or 0)
        turnover = float(item.get("换手率", item.get("turnover_rate", 0)) or 0)
        volume_ratio = float(item.get("量比", item.get("volume_ratio", 1)) or 1)
        result.append(
            StockSnapshot(
                symbol=str(item.get("代码", item.get("symbol", ""))),
                name=str(item.get("名称", item.get("name", "未知标的"))),
                theme=str(item.get("theme", "未分类")),
                close=float(item.get("最新价", item.get("close", 0)) or 0),
                pct_change=pct,
                volume_ratio=volume_ratio,
                turnover_rate=turnover,
                board_height=int(item.get("board_height", 0) or 0),
                is_limit_up=bool(item.get("is_limit_up", pct >= 9.8)),
                is_broken_board=bool(item.get("is_broken_board", False)),
                hot_money_net_buy_million=float(item.get("hot_money_net_buy_million", 0) or 0),
                auction_strength=float(item.get("auction_strength", 0.5) or 0.5),
                seal_strength=float(item.get("seal_strength", 0.5) or 0.5),
                narrative_score=float(item.get("narrative_score", 0.5) or 0.5),
            )
        )
    return result


def try_fetch_with_akshare(limit: int = 50) -> tuple[list[StockSnapshot], str]:
    try:
        import akshare as ak  # type: ignore

        df = ak.stock_zh_a_spot_em()
        df = df.head(limit)
        records = df.to_dict(orient="records")
        stocks = _normalize_records(records)
        return stocks, "akshare"
    except Exception:
        return [], "akshare_unavailable"


def try_fetch_with_eastmoney(limit: int = 50) -> tuple[list[StockSnapshot], str]:
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": limit,
        "po": 1,
        "np": 1,
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": 2,
        "invt": 2,
        "fid": "f3",
        "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f12,f14,f2,f3,f8,f10",
    }
    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"}) as client:
            res = client.get(url, params=params)
            res.raise_for_status()
            payload = res.json()
            diff = payload.get("data", {}).get("diff", [])
            records = []
            for item in diff:
                records.append(
                    {
                        "代码": item.get("f12"),
                        "名称": item.get("f14"),
                        "最新价": item.get("f2", 0),
                        "涨跌幅": item.get("f3", 0),
                        "换手率": item.get("f8", 0),
                        "量比": item.get("f10", 1),
                    }
                )
            stocks = _normalize_records(records)
            return stocks, "eastmoney"
    except Exception:
        return [], "eastmoney_unavailable"


def load_market_data(limit: int = 50) -> tuple[list[StockSnapshot], dict[str, str]]:
    stocks, source = try_fetch_with_akshare(limit=limit)
    if stocks:
        return stocks, {"source": source, "trade_date": str(date.today())}

    stocks, source = try_fetch_with_eastmoney(limit=limit)
    if stocks:
        return stocks, {"source": source, "trade_date": str(date.today())}

    return load_sample_market(), {"source": "sample_fallback", "trade_date": str(date.today())}

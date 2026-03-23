from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import httpx


def fetch_eastmoney_kline(symbol: str, days: int = 10) -> list[dict[str, Any]]:
    secid = _guess_secid(symbol)
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": 101,
        "fqt": 1,
        "secid": secid,
        "beg": (datetime.now() - timedelta(days=days * 3)).strftime("%Y%m%d"),
        "end": datetime.now().strftime("%Y%m%d"),
    }
    with httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"}) as client:
        res = client.get(url, params=params)
        res.raise_for_status()
        payload = res.json()
        klines = payload.get("data", {}).get("klines", [])
        result = []
        for row in klines:
            parts = row.split(",")
            if len(parts) >= 6:
                result.append(
                    {
                        "date": parts[0],
                        "open": float(parts[1]),
                        "close": float(parts[2]),
                        "high": float(parts[3]),
                        "low": float(parts[4]),
                        "volume": float(parts[5]),
                    }
                )
        return result


def _guess_secid(symbol: str) -> str:
    if symbol.startswith(("6", "9")):
        return f"1.{symbol}"
    return f"0.{symbol}"

from __future__ import annotations

import time
from typing import Any, Callable

_CACHE: dict[str, dict[str, Any]] = {}
DEFAULT_TTL_SECONDS = 180.0


def get_or_compute(key: str, compute: Callable[[], Any], ttl_seconds: float = DEFAULT_TTL_SECONDS) -> Any:
    now = time.time()
    item = _CACHE.get(key)
    if item and now - float(item['ts']) <= ttl_seconds:
        return item['value']
    value = compute()
    _CACHE[key] = {
        'ts': now,
        'value': value,
    }
    return value


def clear_cache(prefix: str | None = None) -> dict[str, Any]:
    if not prefix:
        count = len(_CACHE)
        _CACHE.clear()
        return {'cleared': count, 'prefix': None}
    matched = [key for key in list(_CACHE.keys()) if key.startswith(prefix)]
    for key in matched:
        _CACHE.pop(key, None)
    return {'cleared': len(matched), 'prefix': prefix}


def cache_status() -> dict[str, Any]:
    return {
        'size': len(_CACHE),
        'keys': sorted(_CACHE.keys())[:100],
    }

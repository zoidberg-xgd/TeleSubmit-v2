"""
轻量级 TTL 缓存，用于减少重复计算/数据库访问。
"""
import time
from typing import Any, Callable, Tuple


class TTLCache:
    def __init__(self, default_ttl: int = 60, max_size: int = 256) -> None:
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._store: dict[str, Tuple[float, Any]] = {}

    def _evict_if_needed(self) -> None:
        if len(self._store) <= self.max_size:
            return
        # 按过期时间排序，淘汰最早的 10%
        items = sorted(self._store.items(), key=lambda kv: kv[1][0])
        drop = max(1, len(items) // 10)
        for k, _ in items[:drop]:
            self._store.pop(k, None)

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None
        expire_at, value = item
        if expire_at < time.time():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expire_at = time.time() + (ttl or self.default_ttl)
        self._store[key] = (expire_at, value)
        self._evict_if_needed()

    def cached(self, key_builder: Callable[..., str], ttl: int | None = None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                key = key_builder(*args, **kwargs)
                val = self.get(key)
                if val is not None:
                    return val
                val = func(*args, **kwargs)
                self.set(key, val, ttl)
                return val
            return wrapper
        return decorator



import asyncio
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any


class TTLCache:
    """In-memory cache with expiry, shared by all requests in one process.

    Concurrent requests for the same missing key wait for a single fetch instead
    of all hitting ODPT. When running several server processes, swap this for a
    shared cache such as Redis behind the same `get_or_set` interface.
    """

    def __init__(self) -> None:
        self._data: dict[str, tuple[float, Any]] = {}
        self._locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    def _fresh(self, key: str) -> tuple[bool, Any]:
        hit = self._data.get(key)
        if hit and hit[0] > time.monotonic():
            return True, hit[1]
        return False, None

    async def get_or_set(self, key: str, ttl: float, factory: Callable[[], Awaitable[Any]]) -> Any:
        found, value = self._fresh(key)
        if found:
            return value
        async with self._locks[key]:
            found, value = self._fresh(key)
            if found:
                return value
            value = await factory()
            self._data[key] = (time.monotonic() + ttl, value)
            return value

    def clear(self) -> None:
        self._data.clear()

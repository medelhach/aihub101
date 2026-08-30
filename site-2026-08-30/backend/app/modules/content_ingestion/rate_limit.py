import asyncio
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from time import monotonic


class InMemoryRateLimiter:
    """Per-process limiter; distributed runtimes must supply a shared implementation."""

    def __init__(
        self,
        requests_per_minute: int,
        *,
        clock: Callable[[], float] = monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if requests_per_minute < 1:
            raise ValueError("requests_per_minute must be positive")
        self._limit = requests_per_minute
        self._clock = clock
        self._sleep = sleep
        self._requests: defaultdict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def acquire(self, source_id: str) -> None:
        while True:
            wait_for = 0.0
            async with self._lock:
                now = self._clock()
                timestamps = self._requests[source_id]
                while timestamps and timestamps[0] <= now - 60:
                    timestamps.popleft()
                if len(timestamps) < self._limit:
                    timestamps.append(now)
                    return
                wait_for = max(0.0, timestamps[0] + 60 - now)
            await self._sleep(wait_for)

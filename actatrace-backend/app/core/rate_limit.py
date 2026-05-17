from dataclasses import dataclass
from time import time


@dataclass
class RateLimitRule:
    name: str
    path_prefix: str
    limit_per_minute: int
    methods: set[str] | None = None


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[tuple[str, str], list[float]] = {}

    def allow(self, key: str, rule: RateLimitRule) -> bool:
        now = time()
        window_start = now - 60
        bucket_key = (rule.name, key)
        bucket = [timestamp for timestamp in self._buckets.get(bucket_key, []) if timestamp >= window_start]
        if len(bucket) >= rule.limit_per_minute:
            self._buckets[bucket_key] = bucket
            return False
        bucket.append(now)
        self._buckets[bucket_key] = bucket
        return True

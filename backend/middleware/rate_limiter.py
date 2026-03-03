import time
import threading
from typing import Dict, List
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_per_minute: int = 40):
        self.max_per_minute = max_per_minute
        self.window_size = 60
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def cleanup_old_requests(self, client_id: str) -> None:
        now = time.time()
        cutoff = now - self.window_size
        self.requests[client_id] = [t for t in self.requests[client_id] if t > cutoff]

    def is_allowed(self, client_id: str = "default") -> bool:
        with self._lock:
            self.cleanup_old_requests(client_id)

            if len(self.requests[client_id]) >= self.max_per_minute:
                return False

            self.requests[client_id].append(time.time())
            return True

    def get_remaining(self, client_id: str = "default") -> int:
        with self._lock:
            self.cleanup_old_requests(client_id)
            return max(0, self.max_per_minute - len(self.requests[client_id]))

    def get_reset_time(self, client_id: str = "default") -> float:
        with self._lock:
            self.cleanup_old_requests(client_id)
            if not self.requests[client_id]:
                return 0.0

            oldest = min(self.requests[client_id])
            return max(0.0, (oldest + self.window_size) - time.time())


rate_limiter = RateLimiter()

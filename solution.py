import threading
import time
from collections import defaultdict, deque
from typing import Optional


class RateLimiter:
    def __init__(self, max_requests: int, time_window: float):
        """
        Initialize rate limiter.
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)  # key -> deque of timestamps
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        """
        Check if a request for the given key is allowed.
        Args:
            key: Identifier for the request (e.g., user_id, ip_address)
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        
        with self.lock:
            # Clean up old requests outside the time window
            request_times = self.requests[key]
            cutoff_time = current_time - self.time_window
            
            # Remove old timestamps
            while request_times and request_times[0] <= cutoff_time:
                request_times.popleft()
            
            # Check if we can allow this request
            if len(request_times) < self.max_requests:
                # Add current request timestamp
                request_times.append(current_time)
                return True
            else:
                return False
    
    def reset(self, key: str = None) -> None:
        """
        Reset rate limit counters.
        Args:
            key: If provided, reset only this key. If None, reset all keys.
        """
        with self.lock:
            if key is None:
                # Reset all keys
                self.requests.clear()
            else:
                # Reset specific key
                if key in self.requests:
                    self.requests[key].clear()
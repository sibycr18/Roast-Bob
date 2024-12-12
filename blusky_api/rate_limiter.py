import time
from datetime import datetime, timedelta
from typing import Callable, Dict, List
import logging
from functools import wraps

class RateLimiter:
    def __init__(self, max_requests: int = 50, window_minutes: int = 15):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.request_timestamps: Dict[str, List[datetime]] = {}
        self.logger = logging.getLogger(__name__)

    def limit_request(self, endpoint: str = "default"):
        """
        Decorator for rate limiting API requests
        
        Args:
            endpoint: Identifier for different API endpoints
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self._wait_if_needed(endpoint)
                result = func(*args, **kwargs)
                self._record_request(endpoint)
                return result
            return wrapper
        return decorator

    def _wait_if_needed(self, endpoint: str):
        """Wait if rate limit is reached for endpoint"""
        if endpoint not in self.request_timestamps:
            self.request_timestamps[endpoint] = []
            return

        now = datetime.now()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        # Clean old timestamps
        self.request_timestamps[endpoint] = [
            ts for ts in self.request_timestamps[endpoint]
            if ts > window_start
        ]
        
        # Check if we need to wait
        if len(self.request_timestamps[endpoint]) >= self.max_requests:
            oldest_timestamp = self.request_timestamps[endpoint][0]
            wait_seconds = (oldest_timestamp + timedelta(minutes=self.window_minutes) - now).total_seconds()
            
            if wait_seconds > 0:
                self.logger.warning(
                    f"Rate limit reached for {endpoint}. "
                    f"Waiting {wait_seconds:.2f} seconds"
                )
                time.sleep(wait_seconds)

    def _record_request(self, endpoint: str):
        """Record a request for the endpoint"""
        if endpoint not in self.request_timestamps:
            self.request_timestamps[endpoint] = []
        
        self.request_timestamps[endpoint].append(datetime.now())

    def get_remaining_requests(self, endpoint: str = "default") -> int:
        """
        Get remaining requests for endpoint
        
        Args:
            endpoint: API endpoint identifier
        
        Returns:
            Number of remaining requests
        """
        if endpoint not in self.request_timestamps:
            return self.max_requests
        
        now = datetime.now()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        recent_requests = len([
            ts for ts in self.request_timestamps[endpoint]
            if ts > window_start
        ])
        
        return max(0, self.max_requests - recent_requests)

    def reset_limits(self, endpoint: str = None):
        """
        Reset rate limits for specified endpoint or all endpoints
        
        Args:
            endpoint: Optional endpoint to reset
        """
        if endpoint:
            self.request_timestamps.pop(endpoint, None)
        else:
            self.request_timestamps.clear()
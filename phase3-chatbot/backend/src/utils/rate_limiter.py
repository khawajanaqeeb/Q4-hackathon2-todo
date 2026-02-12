import time
import asyncio
from collections import defaultdict
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import threading


class RateLimiter:
    """Rate limiting service to enforce provider-specific rate limits."""

    def __init__(self):
        """
        Initialize Rate Limiter.

        The rate limiter tracks requests per user and provider to enforce limits.
        """
        # Dictionary to store request counts: {(user_id, provider): [(timestamp, weight)]}
        self.requests: Dict[Tuple[str, str], list] = defaultdict(list)
        # Lock for thread safety
        self._lock = threading.Lock()

    def is_allowed(
        self,
        user_id: str,
        provider: str,
        max_requests: int = 100,  # Default: 100 requests
        window_seconds: int = 60  # Default: per minute
    ) -> Tuple[bool, int]:
        """
        Check if a request is allowed based on rate limits.

        Args:
            user_id: User ID making the request
            provider: Provider name
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        with self._lock:
            now = time.time()
            key = (user_id, provider)

            # Remove expired requests
            cutoff_time = now - window_seconds
            self.requests[key] = [
                (timestamp, weight) for timestamp, weight in self.requests[key]
                if timestamp > cutoff_time
            ]

            # Calculate current request count
            current_count = sum(weight for timestamp, weight in self.requests[key])

            # Check if request is allowed
            is_allowed = current_count < max_requests
            remaining = max(0, max_requests - current_count)

            return is_allowed, remaining

    def record_request(
        self,
        user_id: str,
        provider: str,
        weight: int = 1  # Weight of the request (for burst control)
    ) -> bool:
        """
        Record a request in the rate limiter.

        Args:
            user_id: User ID making the request
            provider: Provider name
            weight: Weight of the request (default 1)

        Returns:
            True if request was recorded, False if rate limit exceeded
        """
        with self._lock:
            is_allowed, _ = self.is_allowed(user_id, provider)

            if is_allowed:
                now = time.time()
                key = (user_id, provider)
                self.requests[key].append((now, weight))
                return True

            return False

    def get_wait_time(
        self,
        user_id: str,
        provider: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> float:
        """
        Get the recommended wait time before the next request.

        Args:
            user_id: User ID
            provider: Provider name
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            Recommended wait time in seconds
        """
        with self._lock:
            now = time.time()
            key = (user_id, provider)

            # Remove expired requests
            cutoff_time = now - window_seconds
            self.requests[key] = [
                (timestamp, weight) for timestamp, weight in self.requests[key]
                if timestamp > cutoff_time
            ]

            if len(self.requests[key]) == 0:
                return 0  # No requests in window

            # Sort by timestamp
            sorted_requests = sorted(self.requests[key], key=lambda x: x[0])

            # Calculate how many requests we need to expire to be under the limit
            current_count = sum(weight for timestamp, weight in self.requests[key])

            if current_count < max_requests:
                return 0  # Still under limit

            # Find the earliest timestamp that would bring us under the limit
            excess = current_count - max_requests
            accumulated_weight = 0

            for timestamp, weight in sorted_requests:
                accumulated_weight += weight
                if accumulated_weight >= excess:
                    # Wait until this request expires
                    wait_time = (timestamp + window_seconds) - now
                    return max(0, wait_time)

            # Fallback: wait for the oldest request to expire
            oldest_timestamp = sorted_requests[0][0]
            wait_time = (oldest_timestamp + window_seconds) - now
            return max(0, wait_time)

    def get_quota_status(
        self,
        user_id: str,
        provider: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> Dict[str, any]:
        """
        Get the current quota status for a user and provider.

        Args:
            user_id: User ID
            provider: Provider name
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            Dictionary with quota status information
        """
        with self._lock:
            now = time.time()
            key = (user_id, provider)

            # Remove expired requests
            cutoff_time = now - window_seconds
            self.requests[key] = [
                (timestamp, weight) for timestamp, weight in self.requests[key]
                if timestamp > cutoff_time
            ]

            current_usage = sum(weight for timestamp, weight in self.requests[key])
            remaining = max(0, max_requests - current_usage)
            percentage_used = min(100, (current_usage / max_requests) * 100) if max_requests > 0 else 0

            return {
                "current_usage": current_usage,
                "max_requests": max_requests,
                "remaining": remaining,
                "percentage_used": percentage_used,
                "window_seconds": window_seconds,
                "reset_time": now + window_seconds,
                "is_limited": current_usage >= max_requests
            }

    def reset_quota(self, user_id: str, provider: str):
        """
        Reset the quota for a specific user and provider.

        Args:
            user_id: User ID
            provider: Provider name
        """
        with self._lock:
            key = (user_id, provider)
            if key in self.requests:
                del self.requests[key]

    async def acquire_async(
        self,
        user_id: str,
        provider: str,
        max_requests: int = 100,
        window_seconds: int = 60,
        weight: int = 1
    ) -> bool:
        """
        Async method to acquire permission to make a request with automatic waiting if needed.

        Args:
            user_id: User ID
            provider: Provider name
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            weight: Weight of the request

        Returns:
            True if permission was acquired, False if timeout occurred
        """
        # First, check if we're allowed without waiting
        is_allowed, _ = self.is_allowed(user_id, provider, max_requests, window_seconds)

        if is_allowed:
            # Record the request and return immediately
            return self.record_request(user_id, provider, weight)

        # Calculate wait time
        wait_time = self.get_wait_time(user_id, provider, max_requests, window_seconds)

        if wait_time > 0:
            # Wait for the required time
            await asyncio.sleep(wait_time)

        # Try again after waiting
        is_allowed, _ = self.is_allowed(user_id, provider, max_requests, window_seconds)

        if is_allowed:
            return self.record_request(user_id, provider, weight)

        return False


class QuotaTracker:
    """Track usage against provider-specific quotas."""

    def __init__(self):
        """
        Initialize Quota Tracker.

        Tracks both rate limits and usage quotas (e.g., API call counts, token usage).
        """
        # Dictionary to store usage: {(user_id, provider): {'requests': count, 'tokens': count, 'cost': float}}
        self.usage: Dict[Tuple[str, str], Dict[str, any]] = defaultdict(lambda: {
            'requests': 0,
            'tokens': 0,
            'cost': 0.0,
            'last_reset': time.time()
        })
        self._lock = threading.Lock()

    def track_usage(
        self,
        user_id: str,
        provider: str,
        requests: int = 1,
        tokens: int = 0,
        cost: float = 0.0
    ) -> Dict[str, any]:
        """
        Track usage for a specific user and provider.

        Args:
            user_id: User ID
            provider: Provider name
            requests: Number of requests to add
            tokens: Number of tokens to add
            cost: Cost to add

        Returns:
            Updated usage statistics
        """
        with self._lock:
            key = (user_id, provider)

            self.usage[key]['requests'] += requests
            self.usage[key]['tokens'] += tokens
            self.usage[key]['cost'] += cost

            return self.usage[key].copy()

    def get_usage(
        self,
        user_id: str,
        provider: str
    ) -> Dict[str, any]:
        """
        Get current usage for a specific user and provider.

        Args:
            user_id: User ID
            provider: Provider name

        Returns:
            Current usage statistics
        """
        with self._lock:
            key = (user_id, provider)
            return self.usage[key].copy()

    def reset_usage(self, user_id: str, provider: str):
        """
        Reset usage for a specific user and provider.

        Args:
            user_id: User ID
            provider: Provider name
        """
        with self._lock:
            key = (user_id, provider)
            if key in self.usage:
                self.usage[key] = {
                    'requests': 0,
                    'tokens': 0,
                    'cost': 0.0,
                    'last_reset': time.time()
                }

    def is_within_quota(
        self,
        user_id: str,
        provider: str,
        max_requests: Optional[int] = None,
        max_tokens: Optional[int] = None,
        max_cost: Optional[float] = None
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check if usage is within specified quotas.

        Args:
            user_id: User ID
            provider: Provider name
            max_requests: Maximum allowed requests (None to skip check)
            max_tokens: Maximum allowed tokens (None to skip check)
            max_cost: Maximum allowed cost (None to skip check)

        Returns:
            Tuple of (is_within_quota, current_usage)
        """
        with self._lock:
            current_usage = self.get_usage(user_id, provider)

            within_quota = True

            # Check each limit if specified
            if max_requests is not None and current_usage['requests'] >= max_requests:
                within_quota = False
            if max_tokens is not None and current_usage['tokens'] >= max_tokens:
                within_quota = False
            if max_cost is not None and current_usage['cost'] >= max_cost:
                within_quota = False

            return within_quota, current_usage.copy()


# Global instance for convenience
rate_limiter = RateLimiter()
quota_tracker = QuotaTracker()
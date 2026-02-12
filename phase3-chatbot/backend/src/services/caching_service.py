import redis
import pickle
import json
import hashlib
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import time


class CachingService:
    """Reduce API calls and improve performance through caching."""

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """
        Initialize Caching Service.

        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
        """
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=False)
            # Test connection
            self.redis_client.ping()
        except redis.ConnectionError:
            # Fallback to in-memory cache if Redis is not available
            self.redis_client = None
            self.memory_cache = {}
            self.cache_ttl = {}

    def _generate_key(self, prefix: str, data: Any) -> str:
        """
        Generate a cache key based on prefix and data.

        Args:
            prefix: Cache key prefix
            data: Data to hash for the key

        Returns:
            Generated cache key
        """
        data_str = json.dumps(data, sort_keys=True, default=str) if isinstance(data, (dict, list)) else str(data)
        hash_obj = hashlib.sha256(f"{prefix}:{data_str}".encode())
        return f"{prefix}:{hash_obj.hexdigest()}"

    async def get_cached_data(self, key: str) -> Optional[Any]:
        """
        Retrieve cached data.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return pickle.loads(cached_data)
            except Exception:
                # If Redis fails, continue without cache
                pass
        else:
            # In-memory cache
            if key in self.memory_cache:
                ttl = self.cache_ttl.get(key, 0)
                if time.time() < ttl:
                    return self.memory_cache[key]
                else:
                    # Remove expired item
                    del self.memory_cache[key]
                    del self.cache_ttl[key]

        return None

    async def set_cache(self, key: str, data: Any, ttl_seconds: int = 3600) -> bool:
        """
        Store data in cache.

        Args:
            key: Cache key
            data: Data to cache
            ttl_seconds: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            serialized_data = pickle.dumps(data)

            if self.redis_client:
                # Store in Redis with TTL
                self.redis_client.setex(key, ttl_seconds, serialized_data)
            else:
                # Store in memory with TTL
                self.memory_cache[key] = data
                self.cache_ttl[key] = time.time() + ttl_seconds

            return True
        except Exception:
            return False

    async def invalidate_cache(self, key: str) -> bool:
        """
        Remove stale data from cache.

        Args:
            key: Cache key to invalidate

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.redis_client:
                result = self.redis_client.delete(key)
                return result > 0
            else:
                # Remove from memory cache
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    if key in self.cache_ttl:
                        del self.cache_ttl[key]
                    return True
                return False
        except Exception:
            return False

    async def get_cached_api_call(
        self,
        provider: str,
        endpoint: str,
        params: dict,
        ttl_seconds: int = 300  # 5 minutes default
    ) -> Optional[Any]:
        """
        Get cached API response for a specific provider and endpoint.

        Args:
            provider: API provider name
            endpoint: API endpoint
            params: Request parameters
            ttl_seconds: Time to live in seconds

        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(f"api:{provider}:{endpoint}", params)
        return await self.get_cached_data(key)

    async def cache_api_call(
        self,
        provider: str,
        endpoint: str,
        params: dict,
        response: Any,
        ttl_seconds: int = 300  # 5 minutes default
    ) -> bool:
        """
        Cache an API response.

        Args:
            provider: API provider name
            endpoint: API endpoint
            params: Request parameters
            response: API response to cache
            ttl_seconds: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        key = self._generate_key(f"api:{provider}:{endpoint}", params)
        return await self.set_cache(key, response, ttl_seconds)

    async def invalidate_provider_cache(self, provider: str) -> int:
        """
        Invalidate all cached data for a specific provider.

        Args:
            provider: Provider name

        Returns:
            Number of invalidated cache entries
        """
        if self.redis_client:
            try:
                # Find all keys matching the pattern
                pattern = f"api:{provider}:*"
                keys = self.redis_client.keys(pattern)

                if keys:
                    self.redis_client.delete(*keys)
                    return len(keys)
                return 0
            except Exception:
                return 0
        else:
            # In-memory cache - find and remove matching keys
            count = 0
            keys_to_remove = []

            for key in self.memory_cache:
                if key.startswith(f"api:{provider}:"):
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.memory_cache[key]
                if key in self.cache_ttl:
                    del self.cache_ttl[key]
                count += 1

            return count

    async def get_cache_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if self.redis_client:
            try:
                info = self.redis_client.info()
                return {
                    "backend": "redis",
                    "connected": True,
                    "used_memory": info.get("used_memory_human", "N/A"),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                }
            except Exception:
                return {
                    "backend": "redis",
                    "connected": False
                }
        else:
            return {
                "backend": "memory",
                "connected": True,
                "entry_count": len(self.memory_cache),
                "ttl_entries": len(self.cache_ttl),
            }

    async def clear_cache(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
                self.cache_ttl.clear()
            return True
        except Exception:
            return False
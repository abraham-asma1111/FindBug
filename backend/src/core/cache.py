"""
Redis cache wrapper for FindBug Platform
"""
import json
from typing import Any, Optional

from src.core.config import settings


class CacheService:
    """
    Simple Redis cache wrapper (get / set / delete / expire).
    Falls back gracefully if Redis is not available.
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        """Lazy-initialise Redis client."""
        if self._client is None:
            try:
                import redis
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=3,
                )
                self._client.ping()
            except Exception:
                self._client = None
        return self._client

    # ─── Core operations ─────────────────────────────────────────────────────

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache. Returns None if missing or on error."""
        client = self._get_client()
        if client is None:
            return None
        try:
            raw = client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set a value in cache with a TTL in seconds.
        Returns True on success, False on failure.
        """
        client = self._get_client()
        if client is None:
            return False
        try:
            client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        client = self._get_client()
        if client is None:
            return False
        try:
            client.delete(key)
            return True
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        client = self._get_client()
        if client is None:
            return False
        try:
            return bool(client.exists(key))
        except Exception:
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Update the TTL of an existing key."""
        client = self._get_client()
        if client is None:
            return False
        try:
            return bool(client.expire(key, ttl))
        except Exception:
            return False

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Atomically increment a counter. Returns new value or None."""
        client = self._get_client()
        if client is None:
            return None
        try:
            return client.incrby(key, amount)
        except Exception:
            return None

    def flush_prefix(self, prefix: str) -> int:
        """Delete all keys matching a prefix pattern. Returns deleted count."""
        client = self._get_client()
        if client is None:
            return 0
        try:
            keys = client.keys(f"{prefix}*")
            if keys:
                client.delete(*keys)
            return len(keys)
        except Exception:
            return 0

    # ─── Convenience key builders ─────────────────────────────────────────────

    @staticmethod
    def user_key(user_id: str) -> str:
        return f"user:{user_id}"

    @staticmethod
    def session_key(user_id: str) -> str:
        return f"session:{user_id}"

    @staticmethod
    def rate_limit_key(ip: str, endpoint: str) -> str:
        return f"rate_limit:{ip}:{endpoint}"

    @staticmethod
    def vrt_key(category: str = "all") -> str:
        return f"vrt:{category}"

    @staticmethod
    def leaderboard_key() -> str:
        return "leaderboard:global"


# Singleton instance
cache = CacheService()

"""Cache management utilities for dashboard performance optimization."""

import threading
import time
from functools import wraps


class CacheManager:
    """Simple cache manager with TTL support."""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._lock = threading.Lock()
    
    def get(self, key, default=None):
        """Get value from cache."""
        with self._lock:
            return self._cache.get(key, default)
    
    def set(self, key, value, ttl=300):  # 5 minutes default TTL
        """Set value in cache with TTL."""
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = time.time() + ttl
    
    def delete(self, key):
        """Delete key from cache."""
        with self._lock:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
    
    def clear_expired(self):
        """Clear expired cache entries."""
        current_time = time.time()
        with self._lock:
            expired_keys = [
                key for key, expiry in self._timestamps.items()
                if current_time > expiry
            ]
            for key in expired_keys:
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)
    
    def clear_all(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()


# Global cache instance
dashboard_cache = CacheManager()


def cached(ttl=300, key_func=None):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            result = dashboard_cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            dashboard_cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


def clear_dashboard_cache():
    """Clear all dashboard cache."""
    dashboard_cache.clear_all()


def cleanup_expired_cache():
    """Cleanup expired cache entries."""
    dashboard_cache.clear_expired()
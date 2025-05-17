import time
from datetime import datetime, timedelta
import threading
from app.utils.logger import logger

class CacheEntry:
    """Class representing a single cached item"""
    def __init__(self, value, ttl_seconds=300):
        self.value = value
        self.expiry = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def is_expired(self):
        """Check if the cache entry has expired"""
        return datetime.now() > self.expiry
    
    def get_value(self):
        """Get the cached value"""
        return self.value

class CacheManager:
    """
    Cache manager for storing frequently accessed data to improve performance.
    Uses a singleton pattern and automatic cache expiry.
    """
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CacheManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        """Initialize the cache manager"""
        self._cache = {}
        self._hits = 0
        self._misses = 0
        self._last_cleanup = datetime.now()
        
        # Start the cleanup thread
        self._cleanup_interval = 60  # seconds
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_loop(self):
        """Background thread to periodically clean up expired cache entries"""
        while True:
            time.sleep(self._cleanup_interval)
            try:
                self.cleanup()
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
    
    def cleanup(self):
        """Remove expired cache entries"""
        with self._lock:
            now = datetime.now()
            keys_to_remove = []
            
            for key, entry in self._cache.items():
                if entry.is_expired():
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._cache[key]
            
            if keys_to_remove:
                logger.debug(f"Cache cleanup: removed {len(keys_to_remove)} expired entries")
            
            self._last_cleanup = now
    
    def get(self, key, default=None):
        """
        Get a value from the cache.
        Returns the cached value if it exists and hasn't expired, otherwise returns default.
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                return default
            
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return default
            
            self._hits += 1
            return entry.get_value()
    
    def set(self, key, value, ttl_seconds=300):
        """
        Set a value in the cache with an optional time-to-live.
        Default TTL is 5 minutes (300 seconds).
        """
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl_seconds)
    
    def delete(self, key):
        """Delete a specific key from the cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cached entries"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def get_stats(self):
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests) * 100 if total_requests > 0 else 0
            return {
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total_requests,
                "hit_rate": hit_rate,
                "cached_items": len(self._cache),
                "last_cleanup": self._last_cleanup
            }

# Global access point
global_cache = CacheManager() 
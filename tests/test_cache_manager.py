import unittest
import sys
import os
import time
from datetime import datetime

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.cache_manager import CacheManager, CacheEntry, global_cache

class TestCacheEntry(unittest.TestCase):
    """Test cases for the CacheEntry class"""
    
    def test_init(self):
        """Test initialization of a cache entry"""
        value = "test_value"
        entry = CacheEntry(value, ttl_seconds=10)
        
        self.assertEqual(entry.value, value)
        self.assertFalse(entry.is_expired())
    
    def test_expiry(self):
        """Test that cache entries expire properly"""
        value = "test_value"
        # Set a very short TTL
        entry = CacheEntry(value, ttl_seconds=0.1)
        
        # Should not be expired immediately
        self.assertFalse(entry.is_expired())
        
        # Wait for it to expire
        time.sleep(0.2)
        
        # Should be expired now
        self.assertTrue(entry.is_expired())
    
    def test_get_value(self):
        """Test getting the value from a cache entry"""
        value = "test_value"
        entry = CacheEntry(value)
        
        self.assertEqual(entry.get_value(), value)


class TestCacheManager(unittest.TestCase):
    """Test cases for the CacheManager class"""
    
    def setUp(self):
        """Set up the test environment"""
        # Reset the cache for each test
        global_cache.clear()
    
    def tearDown(self):
        """Clean up after each test"""
        global_cache.clear()
    
    def test_singleton_pattern(self):
        """Test that CacheManager follows the singleton pattern"""
        cache1 = CacheManager()
        cache2 = CacheManager()
        
        self.assertIs(cache1, cache2)
        self.assertIs(cache1, global_cache)
    
    def test_set_and_get(self):
        """Test setting and getting a value"""
        key = "test_key"
        value = "test_value"
        
        # Set a value in the cache
        global_cache.set(key, value)
        
        # Get the value from the cache
        cached_value = global_cache.get(key)
        
        self.assertEqual(cached_value, value)
    
    def test_get_nonexistent_key(self):
        """Test getting a non-existent key returns default"""
        key = "nonexistent_key"
        default = "default_value"
        
        # Get a value that doesn't exist
        cached_value = global_cache.get(key, default)
        
        self.assertEqual(cached_value, default)
    
    def test_delete(self):
        """Test deleting a key from the cache"""
        key = "test_key"
        value = "test_value"
        
        # Set a value in the cache
        global_cache.set(key, value)
        
        # Delete the key
        result = global_cache.delete(key)
        
        # Check the key was deleted successfully
        self.assertTrue(result)
        self.assertIsNone(global_cache.get(key))
    
    def test_delete_nonexistent_key(self):
        """Test deleting a non-existent key"""
        key = "nonexistent_key"
        
        # Delete a key that doesn't exist
        result = global_cache.delete(key)
        
        # Check the delete operation failed
        self.assertFalse(result)
    
    def test_expiry(self):
        """Test that values expire after TTL"""
        key = "expire_key"
        value = "expire_value"
        
        # Set a value with a very short TTL
        global_cache.set(key, value, ttl_seconds=0.1)
        
        # Get the value immediately (should exist)
        self.assertEqual(global_cache.get(key), value)
        
        # Wait for it to expire
        time.sleep(0.2)
        
        # Get the value after expiry (should not exist)
        self.assertIsNone(global_cache.get(key))
    
    def test_clear(self):
        """Test clearing the entire cache"""
        # Set some values in the cache
        global_cache.set("key1", "value1")
        global_cache.set("key2", "value2")
        global_cache.set("key3", "value3")
        
        # Clear the cache
        global_cache.clear()
        
        # Check all keys are gone
        self.assertIsNone(global_cache.get("key1"))
        self.assertIsNone(global_cache.get("key2"))
        self.assertIsNone(global_cache.get("key3"))
    
    def test_stats(self):
        """Test getting cache statistics"""
        # Set some values
        global_cache.set("key1", "value1")
        global_cache.set("key2", "value2")
        
        # Get some values (hits)
        global_cache.get("key1")
        global_cache.get("key2")
        
        # Get some non-existent values (misses)
        global_cache.get("key3")
        
        # Get stats
        stats = global_cache.get_stats()
        
        # Check stats are correct
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["total_requests"], 3)
        self.assertEqual(stats["cached_items"], 2)
        self.assertIsInstance(stats["last_cleanup"], datetime)
        self.assertAlmostEqual(stats["hit_rate"], 66.67, delta=1)


if __name__ == '__main__':
    unittest.main() 
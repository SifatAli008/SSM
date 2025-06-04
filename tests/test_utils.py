import unittest
from datetime import datetime
import os
import json
from app.utils.logger import Logger
logger = Logger()
from app.utils.config_manager import config_manager
from app.utils.database import DatabaseManager
from app.utils.cache_manager import CacheManager

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.log_file = "test.log"
        
    def test_log_creation(self):
        """Test that log file is created and contains messages"""
        test_message = "Test log message"
        logger.info(test_message)
        
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            self.assertIn(test_message, log_content)
            
    def test_log_levels(self):
        """Test different log levels"""
        test_message = "Test message"
        logger.debug(test_message)
        logger.info(test_message)
        logger.warning(test_message)
        logger.error(test_message)
        
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            self.assertIn("DEBUG", log_content)
            self.assertIn("INFO", log_content)
            self.assertIn("WARNING", log_content)
            self.assertIn("ERROR", log_content)

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "app": {
                "name": "Test App",
                "version": "1.0.0"
            },
            "database": {
                "url": "sqlite:///test.db"
            }
        }
        config_manager.load_config(self.test_config)
        
    def test_get_config(self):
        """Test getting configuration values"""
        self.assertEqual(config_manager.get("app.name"), "Test App")
        self.assertEqual(config_manager.get("app.version"), "1.0.0")
        
    def test_set_config(self):
        """Test setting configuration values"""
        config_manager.set("app.name", "New Name")
        self.assertEqual(config_manager.get("app.name"), "New Name")
        
    def test_get_nonexistent(self):
        """Test getting nonexistent config value"""
        self.assertIsNone(config_manager.get("nonexistent.key"))
        self.assertEqual(config_manager.get("nonexistent.key", "default"), "default")

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db_manager = DatabaseManager()
        self.db_manager.initialize(":memory:")
        
    def test_connection(self):
        """Test database connection"""
        self.assertIsNotNone(self.db_manager.engine)
        self.assertTrue(self.db_manager.is_connected())
        
    def test_execute_query(self):
        """Test executing queries"""
        result = self.db_manager.execute_query("SELECT 1")
        self.assertEqual(result[0][0], 1)
        
    def test_transaction(self):
        """Test transaction handling"""
        with self.db_manager.transaction() as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test VALUES (1)")
            
        result = self.db_manager.execute_query("SELECT * FROM test")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 1)

class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.cache = CacheManager()
        
    def test_set_get(self):
        """Test setting and getting cache values"""
        self.cache.set("test_key", "test_value")
        self.assertEqual(self.cache.get("test_key"), "test_value")
        
    def test_expiry(self):
        """Test cache expiry"""
        self.cache.set("test_key", "test_value", ttl=1)
        import time
        time.sleep(2)
        self.assertIsNone(self.cache.get("test_key"))
        
    def test_delete(self):
        """Test cache deletion"""
        self.cache.set("test_key", "test_value")
        self.cache.delete("test_key")
        self.assertIsNone(self.cache.get("test_key"))

if __name__ == '__main__':
    unittest.main()

import pytest
import logging
import json
from pathlib import Path
import os
from datetime import datetime
from app.utils.logger import Logger

@pytest.mark.integration
class TestLogger:
    def test_logger_initialization(self, temp_dir):
        """Test logger initialization and configuration."""
        # Create test config
        config = {
            "logging": {
                "level": "DEBUG",
                "file": os.path.join(temp_dir, "test.log"),
                "max_size": 1024 * 1024,  # 1MB
                "backup_count": 2,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        
        # Initialize logger
        logger = Logger()
        logger.config = config
        logger._setup_logging()
        
        # Test logger instance
        assert logger.logger is not None
        assert logger.logger.level == logging.DEBUG
        assert len(logger.logger.handlers) > 0
        
        # Test log file creation
        log_file = Path(config["logging"]["file"])
        assert log_file.exists()
    
    def test_basic_logging(self, temp_dir):
        """Test basic logging functionality."""
        # Setup logger
        logger = Logger()
        logger.config = {
            "logging": {
                "level": "DEBUG",
                "file": os.path.join(temp_dir, "test.log"),
                "max_size": 1024 * 1024,
                "backup_count": 2,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        logger._setup_logging()
        
        # Test different log levels
        test_message = "Test log message"
        logger.logger.debug(test_message)
        logger.logger.info(test_message)
        logger.logger.warning(test_message)
        logger.logger.error(test_message)
        
        # Verify log file contents
        log_file = Path(logger.config["logging"]["file"])
        log_content = log_file.read_text()
        
        assert "DEBUG" in log_content
        assert "INFO" in log_content
        assert "WARNING" in log_content
        assert "ERROR" in log_content
        assert test_message in log_content
    
    def test_error_logging(self, temp_dir):
        """Test error logging functionality."""
        logger = Logger()
        logger.config = {
            "logging": {
                "level": "ERROR",
                "file": os.path.join(temp_dir, "error.log"),
                "max_size": 1024 * 1024,
                "backup_count": 2,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        logger._setup_logging()
        
        # Test error logging
        test_error = ValueError("Test error")
        logger.log_error(test_error, "Test context")
        
        # Verify error log
        log_file = Path(logger.config["logging"]["file"])
        log_content = log_file.read_text()
        
        assert "ERROR" in log_content
        assert "Test error" in log_content
        assert "Test context" in log_content
        assert "ValueError" in log_content
    
    def test_security_event_logging(self, temp_dir):
        """Test security event logging."""
        logger = Logger()
        logger.config = {
            "logging": {
                "level": "WARNING",
                "file": os.path.join(temp_dir, "security.log"),
                "max_size": 1024 * 1024,
                "backup_count": 2,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        logger._setup_logging()
        
        # Test security event logging
        event_type = "LOGIN_ATTEMPT"
        details = {
            "username": "test_user",
            "ip_address": "192.168.1.1",
            "success": False
        }
        
        logger.log_security_event(event_type, details)
        
        # Verify security log
        log_file = Path(logger.config["logging"]["file"])
        log_content = log_file.read_text()
        
        assert "WARNING" in log_content
        assert event_type in log_content
        assert "test_user" in log_content
        assert "192.168.1.1" in log_content
    
    def test_user_action_logging(self, temp_dir):
        """Test user action logging."""
        logger = Logger()
        logger.config = {
            "logging": {
                "level": "INFO",
                "file": os.path.join(temp_dir, "user_actions.log"),
                "max_size": 1024 * 1024,
                "backup_count": 2,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        logger._setup_logging()
        
        # Test user action logging
        user_id = "123"
        action = "PRODUCT_UPDATE"
        details = {
            "product_id": 456,
            "changes": {"price": 29.99, "stock": 100}
        }
        
        logger.log_user_action(user_id, action, details)
        
        # Verify user action log
        log_file = Path(logger.config["logging"]["file"])
        log_content = log_file.read_text()
        
        assert "INFO" in log_content
        assert user_id in log_content
        assert action in log_content
        assert "product_id" in log_content
        assert "29.99" in log_content
    
    def test_log_rotation(self, temp_dir):
        """Test log file rotation."""
        logger = Logger()
        logger.config = {
            "logging": {
                "level": "INFO",
                "file": os.path.join(temp_dir, "rotation.log"),
                "max_size": 100,  # Small size to force rotation
                "backup_count": 2,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        logger._setup_logging()
        
        # Generate enough logs to trigger rotation
        for i in range(100):
            logger.logger.info(f"Test message {i}" * 10)
        
        # Check for rotated files
        log_dir = Path(temp_dir)
        log_files = list(log_dir.glob("rotation.log*"))
        
        assert len(log_files) > 1  # Should have at least the current and one backup
    
    def test_log_format(self, temp_dir):
        """Test log message formatting."""
        logger = Logger()
        logger.config = {
            "logging": {
                "level": "INFO",
                "file": os.path.join(temp_dir, "format.log"),
                "max_size": 1024 * 1024,
                "backup_count": 2,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        logger._setup_logging()
        
        # Log a test message
        test_message = "Test format message"
        logger.logger.info(test_message)
        
        # Verify log format
        log_file = Path(logger.config["logging"]["file"])
        log_content = log_file.read_text()
        log_line = log_content.strip()
        
        # Check format components
        assert " - " in log_line  # Separator
        assert "INFO" in log_line  # Log level
        assert test_message in log_line  # Message
        assert "app.utils.logger" in log_line  # Logger name
    
    def test_multiple_loggers(self, temp_dir):
        """Test multiple logger instances."""
        # Create multiple loggers
        loggers = []
        for i in range(3):
            logger = Logger()
            logger.config = {
                "logging": {
                    "level": "INFO",
                    "file": os.path.join(temp_dir, f"multi_{i}.log"),
                    "max_size": 1024 * 1024,
                    "backup_count": 2,
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            }
            logger._setup_logging()
            loggers.append(logger)
        
        # Log messages to each logger
        for i, logger in enumerate(loggers):
            logger.logger.info(f"Test message for logger {i}")
        
        # Verify each log file
        for i in range(3):
            log_file = Path(os.path.join(temp_dir, f"multi_{i}.log"))
            assert log_file.exists()
            log_content = log_file.read_text()
            assert f"Test message for logger {i}" in log_content
    
    def test_log_level_filtering(self, temp_dir):
        """Test log level filtering."""
        logger = Logger()
        logger.config = {
            "logging": {
                "level": "WARNING",  # Only WARNING and above
                "file": os.path.join(temp_dir, "level.log"),
                "max_size": 1024 * 1024,
                "backup_count": 2,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        logger._setup_logging()
        
        # Log messages at different levels
        logger.logger.debug("Debug message")
        logger.logger.info("Info message")
        logger.logger.warning("Warning message")
        logger.logger.error("Error message")
        
        # Verify log content
        log_file = Path(logger.config["logging"]["file"])
        log_content = log_file.read_text()
        
        assert "Debug message" not in log_content
        assert "Info message" not in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content 
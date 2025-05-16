import logging
import os
from pathlib import Path
from datetime import datetime

class Logger:
    """
    Utility class for application-wide logging
    """
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        """Set up the logger with proper formatting and file output"""
        # Create logs directory if it doesn't exist
        base_dir = Path(__file__).resolve().parent.parent.parent
        log_dir = os.path.join(base_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)

        # Create a logger
        self._logger = logging.getLogger("SmartShopManager")
        self._logger.setLevel(logging.DEBUG)

        # Create handlers
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        today = datetime.now().strftime("%Y-%m-%d")
        file_handler = logging.FileHandler(os.path.join(log_dir, f"app_{today}.log"))
        file_handler.setLevel(logging.DEBUG)

        # Create formatters
        console_format = logging.Formatter('%(levelname)s - %(message)s')
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add formatters to handlers
        console_handler.setFormatter(console_format)
        file_handler.setFormatter(file_format)

        # Add handlers to logger
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)

        self._logger.info("Logger initialized")

    def debug(self, message):
        """Log a debug message"""
        self._logger.debug(message)

    def info(self, message):
        """Log an info message"""
        self._logger.info(message)

    def warning(self, message):
        """Log a warning message"""
        self._logger.warning(message)

    def error(self, message):
        """Log an error message"""
        self._logger.error(message)

    def critical(self, message):
        """Log a critical message"""
        self._logger.critical(message)


# Singleton instance for easy import
logger = Logger()

# Usage example:
# from app.utils.logger import logger
# logger.info("This is an informational message")
# logger.error("This is an error message")

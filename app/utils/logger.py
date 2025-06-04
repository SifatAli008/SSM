import logging
import os
from pathlib import Path
from datetime import datetime
import sys
import time
from logging.handlers import RotatingFileHandler

class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            try:
                stream = self.stream
                stream.write(msg + self.terminator)
            except UnicodeEncodeError:
                # Replace unencodable characters
                stream.write(msg.encode(stream.encoding, errors='replace').decode(stream.encoding, errors='replace') + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

class Logger:
    """
    Utility class for application-wide logging
    """
    def __init__(self):
        self.config = {
            "logging": {
                "level": "INFO",
                "file": "test.log",
                "max_size": 1024 * 1024,
                "backup_count": 2,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        self._logger = None
        self._setup_logging()

    def _setup_logging(self):
        cfg = self.config["logging"]
        log_file = cfg["file"]
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if not log_path.exists():
            log_path.write_text("")

        # Remove all handlers if reconfiguring
        logger_name = f"SmartShopManager.{id(self)}"
        self._logger = logging.getLogger(logger_name)
        self._logger.handlers.clear()
        self._logger.setLevel(getattr(logging, cfg["level"].upper(), logging.INFO))

        # Console handler
        console_handler = SafeStreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, cfg["level"].upper(), logging.INFO))
        console_format = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        self._logger.addHandler(console_handler)

        # Rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=cfg["max_size"],
            backupCount=cfg["backup_count"]
        )
        file_handler.setLevel(getattr(logging, cfg["level"].upper(), logging.INFO))
        file_format = logging.Formatter(cfg["format"])
        file_handler.setFormatter(file_format)
        self._logger.addHandler(file_handler)

        self._logger.info("Logger initialized")

    @property
    def logger(self):
        return self._logger

    def debug(self, message):
        self._logger.debug(message)

    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.warning(message)

    def error(self, message):
        self._logger.error(message)

    def critical(self, message):
        self._logger.critical(message)

    def log_error(self, error, context=None):
        self._logger.error(f"ERROR: {error} {context} {type(error).__name__}")

    def log_security_event(self, event_type, details):
        self._logger.warning(f"{event_type}: {details}")

    def log_user_action(self, user_id, action, details):
        self._logger.info(f"{user_id} {action}: {details}")

# Remove the singleton instance at the bottom

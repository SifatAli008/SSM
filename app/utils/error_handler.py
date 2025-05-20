import logging
import traceback
from typing import Optional, Type, Callable
from functools import wraps
import sys
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception class for application errors."""
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", details: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert error to dictionary format."""
        return {
            "error_code": self.error_code,
            "message": str(self),
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class DatabaseError(AppError):
    """Database-related errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "DATABASE_ERROR", details)

class AuthenticationError(AppError):
    """Authentication-related errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)

class ValidationError(AppError):
    """Data validation errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)

class ConfigurationError(AppError):
    """Configuration-related errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)

class BackupError(AppError):
    """Backup-related errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "BACKUP_ERROR", details)

class ErrorHandler:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorHandler, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not ErrorHandler._initialized:
            self.error_log_file = Path("logs/errors.json")
            self.error_log_file.parent.mkdir(exist_ok=True)
            self._setup_error_logging()
            ErrorHandler._initialized = True
    
    def _setup_error_logging(self):
        """Set up error logging configuration."""
        if not self.error_log_file.exists():
            with open(self.error_log_file, 'w') as f:
                json.dump([], f)
    
    def handle_error(self, error: Exception, context: str = "") -> dict:
        """Handle an error and return error information."""
        error_info = self._create_error_info(error, context)
        self._log_error(error_info)
        return error_info
    
    def _create_error_info(self, error: Exception, context: str) -> dict:
        """Create error information dictionary."""
        if isinstance(error, AppError):
            error_info = error.to_dict()
        else:
            error_info = {
                "error_code": "UNKNOWN_ERROR",
                "message": str(error),
                "details": {},
                "timestamp": datetime.utcnow().isoformat()
            }
        
        error_info.update({
            "context": context,
            "traceback": traceback.format_exc(),
            "type": error.__class__.__name__
        })
        
        return error_info
    
    def _log_error(self, error_info: dict):
        """Log error to file."""
        try:
            with open(self.error_log_file, 'r+') as f:
                errors = json.load(f)
                errors.append(error_info)
                f.seek(0)
                json.dump(errors, f, indent=4)
                f.truncate()
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
    
    def get_recent_errors(self, limit: int = 10) -> list:
        """Get recent errors from log."""
        try:
            with open(self.error_log_file, 'r') as f:
                errors = json.load(f)
                return errors[-limit:]
        except Exception as e:
            logger.error(f"Failed to read error log: {e}")
            return []
    
    def clear_error_log(self):
        """Clear the error log."""
        try:
            with open(self.error_log_file, 'w') as f:
                json.dump([], f)
        except Exception as e:
            logger.error(f"Failed to clear error log: {e}")

def handle_exceptions(error_handler: Optional[ErrorHandler] = None):
    """Decorator to handle exceptions in functions."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = error_handler or ErrorHandler()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = handler.handle_error(e, f"Error in {func.__name__}")
                logger.error(f"Error in {func.__name__}: {error_info['message']}")
                raise
        return wrapper
    return decorator

def handle_specific_exceptions(*exceptions: Type[Exception]):
    """Decorator to handle specific exceptions in functions."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                error_info = ErrorHandler().handle_error(e, f"Error in {func.__name__}")
                logger.error(f"Error in {func.__name__}: {error_info['message']}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator

def setup_exception_hook():
    """Set up global exception hook."""
    def exception_hook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_info = ErrorHandler().handle_error(
            exc_value,
            "Unhandled exception"
        )
        logger.error(f"Unhandled exception: {error_info['message']}")
    
    sys.excepthook = exception_hook 
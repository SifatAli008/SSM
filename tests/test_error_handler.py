import pytest
from app.utils.error_handler import (
    ErrorHandler, AppError, DatabaseError,
    AuthenticationError, ValidationError,
    ConfigurationError, BackupError,
    handle_exceptions, handle_specific_exceptions
)

class TestErrorHandler:
    def test_error_creation(self):
        """Test creating different types of errors."""
        # Test base AppError
        error = AppError("Test error", "TEST_ERROR", {"detail": "test"})
        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.details == {"detail": "test"}
        
        # Test specific error types
        db_error = DatabaseError("Database error", {"query": "SELECT * FROM users"})
        assert db_error.error_code == "DATABASE_ERROR"
        
        auth_error = AuthenticationError("Auth error", {"username": "test"})
        assert auth_error.error_code == "AUTHENTICATION_ERROR"
        
        val_error = ValidationError("Validation error", {"field": "email"})
        assert val_error.error_code == "VALIDATION_ERROR"
        
        config_error = ConfigurationError("Config error", {"file": "config.json"})
        assert config_error.error_code == "CONFIGURATION_ERROR"
        
        backup_error = BackupError("Backup error", {"path": "backup.zip"})
        assert backup_error.error_code == "BACKUP_ERROR"
    
    def test_error_handling(self, error_handler):
        """Test error handling functionality."""
        # Test handling AppError
        error = AppError("Test error", "TEST_ERROR", {"detail": "test"})
        error_info = error_handler.handle_error(error, "Test context")
        
        assert error_info["error_code"] == "TEST_ERROR"
        assert error_info["message"] == "Test error"
        assert error_info["details"] == {"detail": "test"}
        assert error_info["context"] == "Test context"
        assert "traceback" in error_info
        
        # Test handling standard Exception
        standard_error = ValueError("Standard error")
        error_info = error_handler.handle_error(standard_error, "Standard context")
        
        assert error_info["error_code"] == "UNKNOWN_ERROR"
        assert error_info["message"] == "Standard error"
        assert error_info["context"] == "Standard context"
    
    def test_error_logging(self, error_handler):
        """Test error logging functionality."""
        # Create and handle an error
        error = AppError("Test error", "TEST_ERROR", {"detail": "test"})
        error_handler.handle_error(error, "Test context")
        
        # Get recent errors
        recent_errors = error_handler.get_recent_errors()
        assert len(recent_errors) > 0
        
        # Verify error was logged
        latest_error = recent_errors[-1]
        assert latest_error["error_code"] == "TEST_ERROR"
        assert latest_error["message"] == "Test error"
        assert latest_error["context"] == "Test context"
    
    def test_error_log_cleanup(self, error_handler):
        """Test error log cleanup functionality."""
        # Create some errors
        for i in range(5):
            error = AppError(f"Test error {i}", "TEST_ERROR", {"index": i})
            error_handler.handle_error(error, f"Test context {i}")
        
        # Clear error log
        error_handler.clear_error_log()
        
        # Verify log is empty
        recent_errors = error_handler.get_recent_errors()
        assert len(recent_errors) == 0
    
    def test_error_decorator(self):
        """Test error handling decorator."""
        @handle_exceptions()
        def function_that_raises():
            raise AppError("Test error", "TEST_ERROR")
        
        # Test that error is handled
        with pytest.raises(AppError):
            function_that_raises()
    
    def test_specific_error_decorator(self):
        """Test specific error handling decorator."""
        @handle_specific_exceptions(AppError, ValueError)
        def function_that_raises():
            raise AppError("Test error", "TEST_ERROR")
        
        # Test that specific error is handled
        with pytest.raises(AppError):
            function_that_raises()
        
        # Test that unexpected error is not handled
        @handle_specific_exceptions(AppError)
        def function_that_raises_unexpected():
            raise ValueError("Unexpected error")
        
        with pytest.raises(ValueError):
            function_that_raises_unexpected()
    
    def test_error_conversion(self, error_handler):
        """Test error conversion to dictionary format."""
        error = AppError("Test error", "TEST_ERROR", {"detail": "test"})
        error_dict = error.to_dict()
        
        assert isinstance(error_dict, dict)
        assert error_dict["error_code"] == "TEST_ERROR"
        assert error_dict["message"] == "Test error"
        assert error_dict["details"] == {"detail": "test"}
        assert "timestamp" in error_dict
    
    def test_error_context(self, error_handler):
        """Test error context handling."""
        # Test with different contexts
        contexts = [
            "Database operation",
            "User authentication",
            "Data validation",
            "Configuration loading",
            "Backup process"
        ]
        
        for context in contexts:
            error = AppError(f"Error in {context}", "TEST_ERROR")
            error_info = error_handler.handle_error(error, context)
            assert error_info["context"] == context
    
    def test_error_details(self, error_handler):
        """Test error details handling."""
        # Test with different detail types
        details = [
            {"query": "SELECT * FROM users", "params": [1, 2, 3]},
            {"username": "test", "attempts": 3},
            {"field": "email", "value": "invalid@email"},
            {"file": "config.json", "line": 42},
            {"path": "backup.zip", "size": 1024}
        ]
        
        for detail in details:
            error = AppError("Test error", "TEST_ERROR", detail)
            error_info = error_handler.handle_error(error, "Test context")
            assert error_info["details"] == detail 
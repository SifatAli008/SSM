import pytest
from app.utils.auth import AuthManager
from app.utils.error_handler import AuthenticationError
from datetime import timedelta

@pytest.mark.security
class TestAuthManager:
    def test_password_hashing(self, auth_manager):
        """Test password hashing and verification."""
        password = "TestPass123!"
        hashed = auth_manager.hash_password(password)
        
        assert hashed != password
        assert auth_manager.verify_password(password, hashed)
        assert not auth_manager.verify_password("WrongPass123!", hashed)
    
    def test_password_strength_validation(self, auth_manager):
        """Test password strength validation."""
        # Test valid password
        is_valid, message = auth_manager.validate_password_strength("TestPass123!")
        assert is_valid
        assert message == "Password is strong"
        
        # Test too short password
        is_valid, message = auth_manager.validate_password_strength("Test1!")
        assert not is_valid
        assert "at least 8 characters" in message
        
        # Test missing uppercase
        is_valid, message = auth_manager.validate_password_strength("testpass123!")
        assert not is_valid
        assert "uppercase" in message
        
        # Test missing lowercase
        is_valid, message = auth_manager.validate_password_strength("TESTPASS123!")
        assert not is_valid
        assert "lowercase" in message
        
        # Test missing number
        is_valid, message = auth_manager.validate_password_strength("TestPass!")
        assert not is_valid
        assert "number" in message
        
        # Test missing special character
        is_valid, message = auth_manager.validate_password_strength("TestPass123")
        assert not is_valid
        assert "special character" in message
    
    def test_token_creation_and_verification(self, auth_manager):
        """Test JWT token creation and verification."""
        user_data = {
            "id": 1,
            "username": "test_user",
            "role": "user"
        }
        
        # Create token
        token = auth_manager.create_token(user_data)
        assert token is not None
        
        # Verify token
        decoded = auth_manager.verify_token(token)
        assert decoded is not None
        assert decoded["user_id"] == user_data["id"]
        assert decoded["username"] == user_data["username"]
        assert decoded["role"] == user_data["role"]
    
    def test_invalid_token(self, auth_manager):
        """Test invalid token handling."""
        # Test invalid token
        assert auth_manager.verify_token("invalid_token") is None
        
        # Test expired token
        auth_manager.token_expiry = timedelta(seconds=0)  # Set expiry to 0 to force expiration
        token = auth_manager.create_token({"id": 1, "username": "test", "role": "user"})
        assert auth_manager.verify_token(token) is None 
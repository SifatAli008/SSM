import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not AuthManager._initialized:
            self.secret_key = self._load_or_generate_secret_key()
            self.token_expiry = timedelta(hours=24)
            AuthManager._initialized = True
    
    def _load_or_generate_secret_key(self) -> str:
        """Load or generate a secret key for JWT tokens."""
        key_path = Path("config/secret_key.txt")
        if key_path.exists():
            return key_path.read_text().strip()
        
        # Generate new key
        key_path.parent.mkdir(exist_ok=True)
        new_key = bcrypt.gensalt().decode()
        key_path.write_text(new_key)
        return new_key
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def create_token(self, user_data: Dict[str, Any]) -> str:
        """Create a JWT token for the user."""
        exp_time = int((datetime.utcnow() + self.token_expiry).timestamp())
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'role': user_data['role'],
            'exp': exp_time
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return None
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Validate password strength."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong" 
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.utils.logger import Logger
from app.utils.config_manager import config_manager
from app.utils.database import DatabaseManager
from app.models.base import User, UserCreate, UserUpdate, UserInDB

logger = Logger()

class AuthManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._setup_default_admin()
    
    def _setup_default_admin(self):
        """Set up default admin user if no users exist."""
        with DatabaseManager().get_session() as session:
            if not session.query(User).first():
                admin_user = UserCreate(
                    username=config_manager.get('app.default_admin_username'),
                    email="admin@example.com",
                    password=config_manager.get('app.default_admin_password'),
                    is_admin=True
                )
                self.create_user(admin_user)
                logger.info("Default admin user created")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=config_manager.get('security.token_expire_minutes'))
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            config_manager.get('security.jwt_secret'),
            algorithm=config_manager.get('security.jwt_algorithm')
        )
        return encoded_jwt
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        with DatabaseManager().get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                return None
            if not self.verify_password(password, user.password_hash):
                return None
            return user
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        with DatabaseManager().get_session() as session:
            # Check if username or email already exists
            if session.query(User).filter(User.username == user_data.username).first():
                raise ValueError("Username already exists")
            if session.query(User).filter(User.email == user_data.email).first():
                raise ValueError("Email already exists")
            
            # Create new user
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=self.get_password_hash(user_data.password),
                is_active=user_data.is_active,
                is_admin=user_data.is_admin
            )
            
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            
            logger.info(f"User created: {db_user.username}")
            return db_user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        with DatabaseManager().get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Update user fields
            for field, value in user_data.dict(exclude_unset=True).items():
                if field == 'password' and value:
                    value = self.get_password_hash(value)
                setattr(user, field, value)
            
            session.commit()
            session.refresh(user)
            
            logger.info(f"User updated: {user.username}")
            return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        with DatabaseManager().get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            session.delete(user)
            session.commit()
            
            logger.info(f"User deleted: {user.username}")
            return True
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        with DatabaseManager().get_session() as session:
            return session.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        with DatabaseManager().get_session() as session:
            return session.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        with DatabaseManager().get_session() as session:
            return session.query(User).filter(User.email == email).first()
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token,
                config_manager.get('security.jwt_secret'),
                algorithms=[config_manager.get('security.jwt_algorithm')]
            )
            return payload
        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def check_permission(self, user: User, required_role: str) -> bool:
        """Check if user has required role."""
        if user.is_admin:
            return True
        
        role_access = config_manager.get('app.role_access', {})
        user_role = "staff"  # Default role
        
        if user.is_admin:
            user_role = "admin"
        
        return role_access.get(user_role, 0) >= role_access.get(required_role, 0) 
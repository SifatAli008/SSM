from typing import List, Optional, Dict, Any
from datetime import datetime
from app.utils.logger import Logger
from app.utils.database import DatabaseManager
from app.core.event_system import EventSystem, EventTypes
from app.models.base import User, UserCreate, UserUpdate

logger = Logger()

class UserManager:
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
    
    def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user."""
        try:
            with DatabaseManager().get_session() as session:
                # Check if username or email already exists
                if session.query(User).filter(User.username == user_data.username).first():
                    raise ValueError("Username already exists")
                if session.query(User).filter(User.email == user_data.email).first():
                    raise ValueError("Email already exists")
                
                # Create new user
                user = User(
                    username=user_data.username,
                    email=user_data.email,
                    password_hash=user_data.password_hash,
                    is_active=user_data.is_active,
                    is_admin=user_data.is_admin
                )
                
                session.add(user)
                session.commit()
                session.refresh(user)
                
                # Publish event
                self.event_system.publish(EventTypes.USER_CREATED, {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                })
                
                logger.info(f"User created: {user.username}")
                return user
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        try:
            with DatabaseManager().get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return None
                
                # Update user fields
                for field, value in user_data.dict(exclude_unset=True).items():
                    setattr(user, field, value)
                
                session.commit()
                session.refresh(user)
                
                # Publish event
                self.event_system.publish(EventTypes.USER_UPDATED, {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                })
                
                logger.info(f"User updated: {user.username}")
                return user
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        try:
            with DatabaseManager().get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return False
                
                # Publish event before deletion
                self.event_system.publish(EventTypes.USER_DELETED, {
                    'user_id': user.id,
                    'username': user.username
                })
                
                session.delete(user)
                session.commit()
                
                logger.info(f"User deleted: {user.username}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False
    
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
    
    def list_users(self, is_active: Optional[bool] = None) -> List[User]:
        """List all users, optionally filtered by active status."""
        with DatabaseManager().get_session() as session:
            query = session.query(User)
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            return query.order_by(User.username).all()
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        try:
            with DatabaseManager().get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return False
                
                user.last_login = datetime.utcnow()
                session.commit()
                
                logger.info(f"Updated last login for user: {user.username}")
                return True
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
            return False 
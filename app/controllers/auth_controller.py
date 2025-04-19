import hashlib
import secrets
from app.models.users import User
from config.settings import ROLE_ADMIN, ROLE_MANAGER, ROLE_CASHIER

class AuthController:
    def __init__(self):
        self.current_user = None
        
    def login(self, username, password, role=None):
        hashed_password = self._hash_password(password)
        user = User.get_user_by_username(username)
        if not user or not user.is_active:
            return None
        
        if user.password == hashed_password:
            if role and user.role != role:
                return None
            
            user.update_last_login()
            self.current_user = user
            return user
        return None
        
    def logout(self):
        self.current_user = None
        return True
        
    def register_user(self, username, password, full_name, role=ROLE_CASHIER):
        existing_user = User.get_user_by_username(username)
        if existing_user:
            return None
            
        hashed_password = self._hash_password(password)
        
        new_user = User(
            username=username,
            password=hashed_password,
            full_name=full_name,
            role=role
        )
        
        user_id = new_user.save()
        
        if user_id:
            return new_user
        return None
        
    def change_password(self, user_id, old_password, new_password):
        user = User.get_user_by_id(user_id)
        if not user:
            return False
            
        hashed_old_password = self._hash_password(old_password)
        
        if user.password != hashed_old_password:
            return False
            
        user.password = self._hash_password(new_password)
        user.save()
        
        return True
    
    def get_users_by_role(self, role):
        return User.get_users_by_role(role)
        
    def is_admin(self, user=None):
        if not user:
            user = self.current_user
            
        if not user:
            return False
            
        return user.role == ROLE_ADMIN
        
    def is_manager(self, user=None):
        if not user:
            user = self.current_user
            
        if not user:
            return False
            
        return user.role == ROLE_MANAGER
        
    def is_cashier(self, user=None):
        if not user:
            user = self.current_user
            
        if not user:
            return False
            
        return user.role == ROLE_CASHIER
        
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
        
    def create_initial_admin(self, username, password, full_name):
        users = User.get_all_users()
        if users:
            return False
            
        return self.register_user(username, password, full_name, role=ROLE_ADMIN)
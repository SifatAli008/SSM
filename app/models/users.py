class User:
    """A simple user model that doesn't rely on Firebase"""
    
    def __init__(self, username=None, password=None, full_name=None, role=None, is_active=True, created_at=None):
        self.username = username
        self.password = password
        self.full_name = full_name or "Default User"
        self.role = role or "staff"
        self.is_active = is_active
        self.created_at = created_at
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create a user from dictionary data"""
        return User(
            username=data.get('username'),
            password=data.get('password'),
            full_name=data.get('full_name'),
            role=data.get('role'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at')
        )

    def save(self):
        """Save user to the Firestore database"""
        # This method is not applicable in the simple user model
        pass

    @staticmethod
    def get_user_by_username(username):
        """Retrieve a user by username"""
        # This method is not applicable in the simple user model
        return None

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieve user by ID (same as username in this case)"""
        return User.get_user_by_username(user_id)

    @staticmethod
    def get_users_by_role(role):
        """Retrieve users with a specific role"""
        # This method is not applicable in the simple user model
        return None

    @staticmethod
    def get_all_users():
        """Retrieve all users from Firestore"""
        # This method is not applicable in the simple user model
        return []

    def update_last_login(self):
        """Update the last login timestamp (if needed)"""
        # This method is not applicable in the simple user model
        pass

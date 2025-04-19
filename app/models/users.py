from config.database import FirebaseDB

class User:
    def __init__(self, username, password, full_name, role, is_active=True, created_at=None):
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role
        self.is_active = is_active
        self.created_at = created_at  # ✅ Added to fix TypeError

    def save(self):
        """Save user to the Firestore database"""
        db = FirebaseDB().db
        if not db:
            return None
        
        user_data = {
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at  # ✅ Include timestamp if provided
        }
        
        db.collection("users").document(self.username).set(user_data)
        return True

    @staticmethod
    def get_user_by_username(username):
        """Retrieve a user by username"""
        db = FirebaseDB().db
        if not db:
            return None

        user_doc = db.collection("users").document(username).get()
        if user_doc.exists:
            return User(**user_doc.to_dict())  # ✅ Convert Firestore document to User object
        return None

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieve user by ID (same as username in this case)"""
        return User.get_user_by_username(user_id)

    @staticmethod
    def get_users_by_role(role):
        """Retrieve users with a specific role"""
        db = FirebaseDB().db
        if not db:
            return None
        
        users = db.collection("users").where("role", "==", role).stream()
        return [User(**user.to_dict()) for user in users]

    @staticmethod
    def get_all_users():
        """Retrieve all users from Firestore"""
        db = FirebaseDB().db
        if not db:
            return []

        users = db.collection("users").stream()

        valid_keys = {"username", "password", "full_name", "role", "is_active", "created_at"}
    
        user_list = []
        for user in users:
            user_data = user.to_dict()

            # Ensure required fields exist before creating a User instance
            if "username" not in user_data or "password" not in user_data or "full_name" not in user_data or "role" not in user_data:
                print(f"Skipping invalid user document: {user_data}")  # Debugging line
                continue  # Skip documents missing critical fields

            # Use default values for optional fields
            cleaned_data = {k: user_data.get(k, None) for k in valid_keys}

            user_list.append(User(**cleaned_data))

        return user_list


    def update_last_login(self):
        """Update the last login timestamp (if needed)"""
        pass  # You can implement this feature if required

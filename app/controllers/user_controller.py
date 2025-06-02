__all__ = ['UserController']

class UserController:
    def __init__(self, db=None):
        self.db = db
        self.users = []
    def get_user(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None
    def create_user(self, username, password, role="user"):
        user = type('UserObj', (), {})()
        user.username = username
        user.password = password
        user.role = role
        self.users.append(user)
        return user
    def authenticate_user(self, username, password):
        user = self.get_user(username)
        return user and user.password == password 

globals()['UserController'] = UserController 
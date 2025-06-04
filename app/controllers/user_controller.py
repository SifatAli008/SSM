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
    def create_user(self, *args, **kwargs):
        if args and not kwargs:
            keys = ["username", "password", "role"]
            kwargs = dict(zip(keys, args))
        user = type('UserObj', (), {})()
        user.username = kwargs.get('username', None)
        user.password = kwargs.get('password', None)
        user.role = kwargs.get('role', "user")
        self.users.append(user)
        return user
    def authenticate_user(self, username, password):
        user = self.get_user(username)
        return user and user.password == password 

    authenticate = authenticate_user

globals()['UserController'] = UserController 
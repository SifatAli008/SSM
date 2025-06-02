class User:
    def __init__(self, db=None):
        self.db = db
        self.users = []

    def create(self, username, password, role="user"):
        user = type('UserObj', (), {})()
        user.username = username
        user.password = password
        user.role = role
        user.verify_password = lambda pw: pw == password
        self.users.append(user)
        return user

    def get_by_username(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None 
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Fixing the import path
base_dir = Path(__file__).resolve().parent / 'app'
sys.path.append(str(base_dir))

# Import necessary modules after fixing the path
from config.database import FirebaseDB
from app.controllers.auth_controller import AuthController
from config.settings import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_FULL_NAME
from app.views.login import LoginWindow

def setup_environment():
    """Create necessary folders and prepare environment."""
    required_dirs = ['backups', 'reports']
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
    print("Environment setup completed.")

def initialize_database():
    """Try to connect to Firebase database."""
    try:
        db = FirebaseDB()
        if db.db is not None:
            print("✅ Database initialized successfully.")
            return True
        else:
            print("❌ Database connection returned None.")
            return False
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def create_initial_admin():
    """Attempt to create default admin if not already exists."""
    try:
        auth_controller = AuthController()
        result = auth_controller.create_initial_admin(
            username=DEFAULT_ADMIN_USERNAME,
            password=DEFAULT_ADMIN_PASSWORD,
            full_name=DEFAULT_ADMIN_FULL_NAME
        )
        if result:
            print(f"[✔] Admin user created: {DEFAULT_ADMIN_USERNAME}")
            print("⚠️  Please change the default password after first login.")
        else:
            print("Admin user already exists or creation failed.")
    except Exception as e:
        print(f"❌ Error while creating initial admin: {e}")

def launch_app():
    """Start the PyQt application."""
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

def main():
    """Main application entry point."""
    print("Launching Smart Shop Manager...")

    # Step 1: Set up the environment (folders)
    setup_environment()

    # Step 2: Initialize the database (Firebase)
    if not initialize_database():
        print("❌ Failed to connect to database. Exiting...")
        return

    # Step 3: Create initial admin user (if not already created)
    create_initial_admin()

    # Step 4: Launch the PyQt application
    launch_app()

if __name__ == "__main__":
    main()

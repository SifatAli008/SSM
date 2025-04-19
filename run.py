import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Fixing the import path
base_dir = Path(__file__).parent / 'app'
sys.path.append(str(base_dir))

from config.database import FirebaseDB
from app.controllers.auth_controller import AuthController
from config.settings import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_FULL_NAME
from app.views.login import LoginWindow

def setup_environment():
    """Set up application environment"""
    # Create necessary directories
    os.makedirs('backups', exist_ok=True)
    os.makedirs('reports', exist_ok=True)

def initialize_database():
    """Initialize database connection"""
    db = FirebaseDB()
    return db.db is not None

def create_initial_admin():
    """Create initial admin user if none exists"""
    auth_controller = AuthController()
    result = auth_controller.create_initial_admin(
        username=DEFAULT_ADMIN_USERNAME,
        password=DEFAULT_ADMIN_PASSWORD,
        full_name=DEFAULT_ADMIN_FULL_NAME
    )
    
    if result:
        print(f"Initial admin user created. Username: {DEFAULT_ADMIN_USERNAME}")
        print("Please change the default password immediately after first login.")
    else:
        print("Admin user already exists or failed to create.")

def main():
    """Main application entry point"""
    # Setup environment
    setup_environment()
    
    # Initialize database
    if not initialize_database():
        print("Failed to initialize database. Exiting...")
        return
        
    # Create initial admin user
    create_initial_admin()
    
    # Start the GUI application
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()

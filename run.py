import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
import traceback

# Add the current directory to path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

print("Starting Smart Shop Manager...")

try:
    # Import necessary modules after fixing the path
    from app.views.login import LoginWindow
    from app.utils.database import DatabaseManager
    from config.init_db import create_db
    from app.utils.theme_manager import ThemeManager, ThemeType
    print("Modules imported successfully")
except Exception as e:
    print(f"Error importing modules: {e}")
    traceback.print_exc()
    sys.exit(1)

def setup_environment():
    """Create necessary folders and prepare environment."""
    print("Setting up environment...")
    required_dirs = ['backups', 'reports', 'logs', 'data']
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Create icon directory if it doesn't exist
    os.makedirs("app/assets/icons", exist_ok=True)
    
    print("Environment setup completed.")

def initialize_database():
    """Set up the SQLite database."""
    print("Initializing database...")
    try:
        # Create or ensure the database exists
        create_db()
        
        # Test the database connection
        db = DatabaseManager.get_qt_connection()
        if db and db.isOpen():
            print("✅ Database initialized successfully.")
            return True
        else:
            print("❌ Database connection failed.")
            return False
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        traceback.print_exc()
        return False

def launch_app():
    """Start the PyQt application."""
    print("Launching application UI...")
    app = QApplication(sys.argv)
    
    # Apply theme before creating any windows
    ThemeManager.apply_theme(ThemeType.LIGHT)
    
    login_window = LoginWindow()
    
    # Automatically fill admin credentials for testing
    login_window.username_input.setText("admin")
    login_window.password_input.setText("adminPass123")
    login_window.set_role_selection("admin")
    
    login_window.show()
    print("Application window displayed")
    sys.exit(app.exec_())

def main():
    """Main application entry point."""
    print("Launching Smart Shop Manager...")

    # Step 1: Set up the environment (folders)
    setup_environment()

    # Step 2: Initialize the database (SQLite)
    if not initialize_database():
        print("❌ Failed to connect to database. Will try to continue anyway...")
    
    # Step 3: Launch the PyQt application
    app = QApplication(sys.argv)
    
    # Create and show the login window
    login_window = LoginWindow()
    login_window.show()
    
    # Set up cleanup on exit
    def cleanup():
        from app.utils.database import DatabaseManager
        DatabaseManager.close_connections()
    
    app.aboutToQuit.connect(cleanup)
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()

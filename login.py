import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Add the current directory to path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from app.views.login import LoginWindow
from app.utils.database import DatabaseManager
from config.init_db import create_db

def main():
    # Initialize the database
    print("Initializing database...")
    try:
        create_db()
        print("Database initialized")
    except Exception as e:
        print(f"Database initialization issue: {e}")
        # Continue anyway
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Show the login window
    print("Opening login window...")
    login_window = LoginWindow()
    
    # Set the admin credentials automatically for easy access
    login_window.username_input.setText("admin")
    login_window.password_input.setText("adminPass123")
    login_window.set_role_selection("admin")
    
    login_window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 
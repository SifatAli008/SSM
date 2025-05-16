"""
Smart Shop Manager - UI Test Script
This script launches the application with the new UI components and theme support.
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Add the current directory to path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

def main():
    """Main application entry point."""
    try:
        # Import necessary modules
        print("Importing modules...")
        from app.models.users import User
        from app.views.main_window import MainWindow
        from app.utils.database import DatabaseManager
        from config.init_db import create_db
        from app.utils.theme_manager import ThemeManager, ThemeType
        
        print("Setting up environment...")
        required_dirs = ['backups', 'reports', 'logs', 'data']
        for directory in required_dirs:
            os.makedirs(directory, exist_ok=True)
        
        # Create icon directory if it doesn't exist
        os.makedirs("app/assets/icons", exist_ok=True)
        
        # Initialize database
        print("Initializing database...")
        try:
            create_db()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization issue: {e}")
            # Continue anyway
        
        # Create the application
        app = QApplication(sys.argv)
        
        # Apply theme
        ThemeManager.apply_theme(ThemeType.LIGHT)
        
        # Create a test user (skipping authentication)
        current_user = User(username="admin", full_name="Admin User", role="admin")
        
        # Create and show the main window
        print("Opening main window...")
        main_window = MainWindow(current_user)
        main_window.showMaximized()
        
        # Start the application
        print("Application started")
        sys.exit(app.exec_())
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 
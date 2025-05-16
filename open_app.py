import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
import traceback

# Add the current directory to path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

def main():
    try:
        # Import classes
        print("Importing modules...")
        from app.models.users import User
        from app.views.main_window import MainWindow
        from app.utils.database import DatabaseManager
        from config.init_db import create_db
        print("Imports successful")
        
        # Initialize the database
        print("Initializing database...")
        try:
            create_db()
            print("Database initialized")
        except Exception as e:
            print(f"Database initialization issue: {e}")
            traceback.print_exc()
            # Continue anyway
        
        # Create the application
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        
        # Create a test user (skipping authentication)
        print("Creating test user...")
        current_user = User(full_name="Admin User", role="admin")
        
        # Create and show the main window
        print("Opening main window...")
        main_window = MainWindow(current_user)
        main_window.show()
        
        print("Starting event loop...")
        # Start the application event loop
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 
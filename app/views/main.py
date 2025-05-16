# main.py
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(base_dir))

from PyQt5.QtWidgets import QApplication, QMessageBox
from app.models.users import User
from app.views.main_window import MainWindow
from app.utils.database import DatabaseManager

def main():
    app = QApplication(sys.argv)

    # ✅ Initialize the SQLite connection before anything else
    db = DatabaseManager.get_qt_connection()
    if not db or not db.isOpen():
        QMessageBox.critical(None, "Database Error", 
                           "Failed to connect to the database. The application will now exit.")
        print("⚠️ Exiting app — Database failed to open.")
        return

    current_user = User(full_name="Sifat Ali", role="admin")
    main_window = MainWindow(current_user)
    main_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

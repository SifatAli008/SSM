# main.py
import sys
from PyQt5.QtWidgets import QApplication
from models.users import User
from views.main_window import MainWindow
from config.sqlite_db import init_sqlite_connection  # 👈 import it

def main():
    app = QApplication(sys.argv)

    # ✅ Initialize the SQLite connection before anything else
    db = init_sqlite_connection()
    if not db or not db.isOpen():
        print("⚠️ Exiting app — Database failed to open.")
        return

    current_user = User(full_name="Sifat Ali", role="admin")
    main_window = MainWindow(current_user)
    main_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

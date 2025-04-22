import sys
from PyQt5.QtWidgets import QApplication
from models.users import User
from views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    # Dummy current_user for testing — replace with actual login logic
    current_user = User(full_name="Sifat Ali", role="admin")
    
    main_window = MainWindow(current_user)
    main_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

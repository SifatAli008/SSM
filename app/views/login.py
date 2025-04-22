import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QFrame, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from controllers.auth_controller import AuthController
from views.main_window import MainWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Smart Shop Manager - Login')
        self.setFixedSize(460, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton#loginButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
                padding: 12px;
            }
            QPushButton#loginButton:hover {
                background-color: #2980b9;
            }
            QPushButton#adminLink {
                color: #3498db;
                text-decoration: underline;
                font-size: 13px;
            }
            QPushButton#adminLink:hover {
                color: #2980b9;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # Title
        title = QLabel('Smart Shop Manager')
        title.setFont(QFont('Segoe UI', 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel('Login to access your dashboard')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 13px;")
        layout.addWidget(subtitle)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #ccc;")
        layout.addWidget(line)

        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)

        # Username
        username_label = QLabel("Username")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")

        # Password
        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)

        # Remember Me + Forgot Password
        remember_forgot_layout = QHBoxLayout()
        self.remember_me = QCheckBox("Remember me")
        self.forgot_password = QPushButton("Forgot password?")
        self.forgot_password.setObjectName('adminLink')
        self.forgot_password.setFlat(True)
        self.forgot_password.setCursor(Qt.PointingHandCursor)

        remember_forgot_layout.addWidget(self.remember_me)
        remember_forgot_layout.addStretch()
        remember_forgot_layout.addWidget(self.forgot_password)
        form_layout.addLayout(remember_forgot_layout)

        # Role Selection
        role_label = QLabel("Login as:")
        role_label.setFont(QFont('Segoe UI', 11))
        form_layout.addWidget(role_label)

        roles_layout = QHBoxLayout()
        self.admin_button = self.make_role_button("Admin", True)
        self.manager_button = self.make_role_button("Manager")
        self.cashier_button = self.make_role_button("Cashier")

        self.admin_button.clicked.connect(lambda: self.set_role_selection('admin'))
        self.manager_button.clicked.connect(lambda: self.set_role_selection('manager'))
        self.cashier_button.clicked.connect(lambda: self.set_role_selection('cashier'))

        roles_layout.addWidget(self.admin_button)
        roles_layout.addWidget(self.manager_button)
        roles_layout.addWidget(self.cashier_button)
        form_layout.addLayout(roles_layout)

        # Login button
        self.login_button = QPushButton("LOGIN")
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)

        layout.addLayout(form_layout)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        footer_label = QLabel("Need help? Contact the ")
        self.admin_link = QPushButton("System Administrator")
        self.admin_link.setObjectName("adminLink")
        self.admin_link.setFlat(True)
        self.admin_link.setCursor(Qt.PointingHandCursor)

        footer.addWidget(footer_label)
        footer.addWidget(self.admin_link)
        footer.addStretch()
        layout.addLayout(footer)

        # Events
        self.setLayout(layout)
        self.username_input.setFocus()
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        self.password_input.returnPressed.connect(self.handle_login)
        self.admin_link.clicked.connect(self.contact_admin)
        self.forgot_password.clicked.connect(self.reset_password)

    def make_role_button(self, label, checked=False):
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setMinimumHeight(36)
        btn.setStyleSheet("""
            QPushButton {
                padding: 6px 15px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #f4f4f4;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
            }
        """)
        return btn

    def set_role_selection(self, role):
        self.admin_button.setChecked(role == 'admin')
        self.manager_button.setChecked(role == 'manager')
        self.cashier_button.setChecked(role == 'cashier')

    def get_selected_role(self):
        if self.admin_button.isChecked():
            return 'admin'
        elif self.manager_button.isChecked():
            return 'manager'
        return 'cashier'

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        role = self.get_selected_role()

        if not username:
            QMessageBox.warning(self, "Input Error", "Please enter your username")
            return
        if not password:
            QMessageBox.warning(self, "Input Error", "Please enter your password")
            return

        self.login_button.setText("Signing in...")
        self.login_button.setEnabled(False)
        QApplication.processEvents()

        try:
            user = self.auth_controller.login(username, password, role)
            if user:
                QMessageBox.information(self, "Login Successful",
                                        f"Welcome {user.full_name}!\nAccessing {role.capitalize()} Dashboard")
                self.open_appropriate_window(user)
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password for selected role.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        self.login_button.setText("LOGIN")
        self.login_button.setEnabled(True)

    def open_appropriate_window(self, user):
        self.main_window = MainWindow(user)
        self.main_window.logout_requested.connect(self.show_again)
        self.main_window.show()
        self.close()

    def show_again(self):
        self.show()

    def contact_admin(self):
        QMessageBox.information(self, 'Contact Administrator',
                                 'Please contact:\nSystem Admin\nadmin@smartshop.com\nPhone: (555) 123-4567')

    def reset_password(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, 'Reset Password', 'Enter your username first')
            return
        QMessageBox.information(self, 'Reset Link',
                                f'A reset link has been sent to the email linked to {username}.')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

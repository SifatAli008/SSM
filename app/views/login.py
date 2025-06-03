import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QFrame, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from app.controllers.auth_controller import AuthController
from app.views.main_window import MainWindow
from app.views.widgets.components import Button, Card
from app.utils.theme_manager import ThemeManager, ThemeType
from app.utils.ui_helpers import show_error


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        # Explicitly apply light theme
        ThemeManager.apply_theme(ThemeType.LIGHT)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Smart Shop Manager - Login')
        self.setFixedSize(460, 600)
        
        # Use container widget for proper styling
        container = QWidget(self)
        container.setGeometry(0, 0, 460, 600)
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {ThemeManager.get_color('background')};
                font-family: '{ThemeManager.FONTS['family']}';
                color: {ThemeManager.get_color('text_primary')};
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # Title
        title_container = QWidget()
        title_container.setStyleSheet("background-color: transparent;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Logo/icon
        logo_label = QLabel("🏪")
        logo_label.setFont(QFont(ThemeManager.FONTS["family"], 36, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet(f"color: {ThemeManager.get_color('text_primary')}; background-color: transparent;")
        title_layout.addWidget(logo_label)
        
        title = QLabel('Smart Shop Manager')
        title.setFont(QFont(ThemeManager.FONTS["family"], 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {ThemeManager.get_color('text_primary')}; background-color: transparent;")
        title_layout.addWidget(title)

        subtitle = QLabel('Login to access your dashboard')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')}; font-size: 13px; background-color: transparent;")
        title_layout.addWidget(subtitle)

        layout.addWidget(title_container)

        # Login card with form
        login_card = Card()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)

        # Username
        username_label = QLabel("Username")
        username_label.setStyleSheet(f"color: {ThemeManager.get_color('text_primary')}; background-color: transparent;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(40)

        # Password
        password_label = QLabel("Password")
        password_label.setStyleSheet(f"color: {ThemeManager.get_color('text_primary')}; background-color: transparent;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)

        # Remember Me + Forgot Password
        remember_forgot_layout = QHBoxLayout()
        self.remember_me = QCheckBox("Remember me")
        self.remember_me.setStyleSheet(f"color: {ThemeManager.get_color('text_primary')}; background-color: transparent;")
        self.forgot_password = QPushButton("Forgot password?")
        self.forgot_password.setFlat(True)
        self.forgot_password.setCursor(Qt.PointingHandCursor)
        self.forgot_password.setStyleSheet(f"""
            QPushButton {{
                color: {ThemeManager.get_color('primary')};
                text-decoration: underline;
                font-size: 13px;
                background: transparent;
                border: none;
            }}
        """)

        remember_forgot_layout.addWidget(self.remember_me)
        remember_forgot_layout.addStretch()
        remember_forgot_layout.addWidget(self.forgot_password)
        form_layout.addLayout(remember_forgot_layout)
        form_layout.addSpacing(10)

        # Role Selection
        role_label = QLabel("Login as:")
        role_label.setFont(QFont(ThemeManager.FONTS['family'], 11))
        role_label.setStyleSheet(f"color: {ThemeManager.get_color('text_primary')}; background-color: transparent;")
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
        form_layout.addSpacing(10)

        # Login button using our Button component
        self.login_button = Button("LOGIN", variant="primary")
        self.login_button.setMinimumHeight(45)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)

        login_card.layout.addLayout(form_layout)
        layout.addWidget(login_card)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        footer_label = QLabel("Need help? Contact the ")
        footer_label.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')}; background-color: transparent;")
        self.admin_link = QPushButton("System Administrator")
        self.admin_link.setFlat(True)
        self.admin_link.setCursor(Qt.PointingHandCursor)
        self.admin_link.setStyleSheet(f"""
            QPushButton {{
                color: {ThemeManager.get_color('primary')};
                text-decoration: underline;
                font-size: 13px;
                background: transparent;
                border: none;
            }}
            QPushButton:hover {{
                color: {ThemeManager.get_color('primary_dark')};
            }}
        """)

        footer.addWidget(footer_label)
        footer.addWidget(self.admin_link)
        footer.addStretch()
        layout.addLayout(footer)

        # Events
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
        btn.setStyleSheet(f"""
            QPushButton {{
                padding: 6px 15px;
                border: 1px solid {ThemeManager.get_color('border')};
                border-radius: {ThemeManager.BORDER_RADIUS['small']}px;
                background-color: {ThemeManager.get_color('card')};
                color: {ThemeManager.get_color('text_primary')};
            }}
            QPushButton:checked {{
                background-color: {ThemeManager.get_color('primary')};
                color: white;
                border: 1px solid {ThemeManager.get_color('primary_dark')};
            }}
            QPushButton:hover:!checked {{
                background-color: {ThemeManager.get_color('hover')};
            }}
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
            show_error(self, "Please enter your username", title="Input Error")
            return
        if not password:
            show_error(self, "Please enter your password", title="Input Error")
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
                show_error(self, "Invalid username or password for selected role.", title="Login Failed")
        except Exception as e:
            show_error(self, str(e))

        self.login_button.setText("LOGIN")
        self.login_button.setEnabled(True)

    def open_appropriate_window(self, user):
        self.main_window = MainWindow(user)
        self.main_window.logout_requested.connect(self.show_again)
        self.main_window.show()
        self.hide()

    def show_again(self):
        self.password_input.clear()
        self.show()

    def contact_admin(self):
        QMessageBox.information(self, 'Contact Administrator',
                                 'Please contact:\nSystem Admin\nadmin@smartshop.com\nPhone: (555) 123-4567')

    def reset_password(self):
        username = self.username_input.text().strip()
        if not username:
            show_error(self, 'Enter your username first', title='Reset Password')
            return
        QMessageBox.information(self, 'Reset Link',
                                f'A reset link has been sent to the email linked to {username}.')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QFrame, QSizePolicy, QCheckBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette

from controllers.auth_controller import AuthController

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle('Smart Shop Manager - Login')
        self.setFixedSize(500, 480)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                padding: 12px;
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton#loginButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
                padding: 8px;
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
            QCheckBox {
                font-size: 13px;
                color: #555555;
            }
        """)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(40, 35, 40, 35)
        
        # Logo area
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        # You can add your logo here
        # logo_label.setPixmap(QPixmap("assets/images/logo.png").scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)
        main_layout.addLayout(logo_layout)
        
        # Title area
        title_label = QLabel('Smart Shop Manager')
        title_label.setFont(QFont('Segoe UI', 26, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel('Login to access your dashboard')
        subtitle_label.setFont(QFont('Segoe UI', 13))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666666; margin-bottom: 5px;")
        main_layout.addWidget(subtitle_label)
        
        # Add horizontal separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        main_layout.addWidget(separator)
        
        # Create a card-like container for login form
        login_card = QFrame()
        login_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            }
        """)
        login_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Login form layout
        login_layout = QVBoxLayout(login_card)
        login_layout.setContentsMargins(28, 28, 28, 28)
        login_layout.setSpacing(16)
        
        # Username field
        username_label = QLabel('Username')
        username_label.setFont(QFont('Segoe UI', 11))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter your username')
        self.username_input.setMinimumHeight(45)
        login_layout.addWidget(username_label)
        login_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel('Password')
        password_label.setFont(QFont('Segoe UI', 11))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter your password')
        self.password_input.setMinimumHeight(45)
        self.password_input.setEchoMode(QLineEdit.Password)
        login_layout.addWidget(password_label)
        login_layout.addWidget(self.password_input)
        
        # Add "Remember me" checkbox and "Forgot password" link
        remember_forgot_layout = QHBoxLayout()
        self.remember_me = QCheckBox("Remember me")
        self.forgot_password = QPushButton("Forgot password?")
        self.forgot_password.setObjectName('adminLink')
        self.forgot_password.setFlat(True)
        remember_forgot_layout.addWidget(self.remember_me)
        remember_forgot_layout.addStretch()
        remember_forgot_layout.addWidget(self.forgot_password)
        login_layout.addLayout(remember_forgot_layout)
        
        # Role selection label
        role_label = QLabel('Login as:')
        role_label.setFont(QFont('Segoe UI', 11))
        login_layout.addWidget(role_label)
        
        # Role selection buttons
        role_buttons_layout = QHBoxLayout()
        
        self.admin_button = QPushButton('Admin')
        self.admin_button.setCheckable(True)
        self.admin_button.setChecked(True)
        self.admin_button.setMinimumHeight(38)
        self.admin_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 13px;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
            }
            QPushButton:hover:!checked {
                background-color: #e8e8e8;
            }
        """)
        
        self.manager_button = QPushButton('Manager')
        self.manager_button.setCheckable(True)
        self.manager_button.setMinimumHeight(38)
        self.manager_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 13px;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
            }
            QPushButton:hover:!checked {
                background-color: #e8e8e8;
            }
        """)
        
        self.cashier_button = QPushButton('Cashier')
        self.cashier_button.setCheckable(True)
        self.cashier_button.setMinimumHeight(38)
        self.cashier_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 13px;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
            }
            QPushButton:hover:!checked {
                background-color: #e8e8e8;
            }
        """)
        
        # Connect button signals to keep only one checked
        self.admin_button.clicked.connect(lambda: self.set_role_selection('admin'))
        self.manager_button.clicked.connect(lambda: self.set_role_selection('manager'))
        self.cashier_button.clicked.connect(lambda: self.set_role_selection('cashier'))
        
        role_buttons_layout.addWidget(self.admin_button)
        role_buttons_layout.addWidget(self.manager_button)
        role_buttons_layout.addWidget(self.cashier_button)
        login_layout.addLayout(role_buttons_layout)
        
        # Add space before login button
        login_layout.addSpacing(5)
        
        # Add login button
        self.login_button = QPushButton('LOGIN')
        self.login_button.setObjectName('loginButton')
        self.login_button.setMinimumHeight(50)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        login_layout.addWidget(self.login_button)
        
        # Add the login card to the main layout
        main_layout.addWidget(login_card)
        
        # Footer with contact link
        footer_layout = QHBoxLayout()
        footer_label = QLabel("Need help? Contact the")
        self.admin_link = QPushButton("System Administrator")
        self.admin_link.setObjectName('adminLink')
        self.admin_link.setFlat(True)
        self.admin_link.setCursor(Qt.PointingHandCursor)
        footer_layout.addStretch()
        footer_layout.addWidget(footer_label)
        footer_layout.addWidget(self.admin_link)
        footer_layout.addStretch()
        main_layout.addLayout(footer_layout)
        
        # Connect events
        self.admin_link.clicked.connect(self.contact_admin)
        self.forgot_password.clicked.connect(self.reset_password)
        
        # Set the main layout
        self.setLayout(main_layout)
        
        # Set initial focus and enter key functionality
        self.username_input.setFocus()
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        self.password_input.returnPressed.connect(self.handle_login)
    
    def set_role_selection(self, role):
        # Update button states based on role selection
        self.admin_button.setChecked(role == 'admin')
        self.manager_button.setChecked(role == 'manager')
        self.cashier_button.setChecked(role == 'cashier')
    
    def get_selected_role(self):
        if self.admin_button.isChecked():
            return 'admin'
        elif self.manager_button.isChecked():
            return 'manager'
        else:
            return 'cashier'
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        selected_role = self.get_selected_role()
        
        # Validate inputs
        if not username:
            QMessageBox.warning(self, 'Input Error', 'Please enter your username')
            self.username_input.setFocus()
            return
            
        if not password:
            QMessageBox.warning(self, 'Input Error', 'Please enter your password')
            self.password_input.setFocus()
            return
            
        # Show loading indicator (could implement with a progress bar or spinner)
        self.login_button.setEnabled(False)
        self.login_button.setText('Signing in...')
        QApplication.processEvents()  # Update UI
        
        # Attempt login with role-based authentication
        try:
            user = self.auth_controller.login(username, password, selected_role)
            
            if user:
                if self.remember_me.isChecked():
                    # Save username for next time (implementation would be needed)
                    print(f"Remember login for: {username}")
                
                # Show success message
                QMessageBox.information(self, 'Login Successful', 
                                    f'Welcome, {user.full_name}!\nAccessing {user.role.capitalize()} Dashboard')
                
                # Open the appropriate window based on user role
                self.open_appropriate_window(user)
            else:
                self.login_button.setEnabled(True)
                self.login_button.setText('LOGIN')
                QMessageBox.warning(self, 'Authentication Failed', 
                                'Invalid username or password for the selected role')
                self.password_input.clear()
                self.password_input.setFocus()
        
        except Exception as e:
            self.login_button.setEnabled(True)
            self.login_button.setText('LOGIN')
            QMessageBox.critical(self, 'System Error', 
                            f'An error occurred during login: {str(e)}')
            
    def open_appropriate_window(self, user):
        # This method would open different windows based on user role
        try:
            if user.role == 'admin':
                # from views.admin_dashboard import AdminDashboard
                # self.main_window = AdminDashboard(user)
                print(f"Opening Admin Dashboard for {user.full_name}")
            elif user.role == 'manager':
                # from views.manager_dashboard import ManagerDashboard
                # self.main_window = ManagerDashboard(user)
                print(f"Opening Manager Dashboard for {user.full_name}")
            elif user.role == 'cashier':
                # from views.cashier_interface import CashierInterface
                # self.main_window = CashierInterface(user)
                print(f"Opening Cashier Interface for {user.full_name}")
            
            # self.main_window.show()
            # self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to open dashboard: {str(e)}')
    
    def contact_admin(self):
        # Show contact information for the system administrator
        QMessageBox.information(self, 'Contact Administrator',
                             'For assistance, please contact:\n\n'
                             'System Administrator\n'
                             'Email: admin@smartshop.com\n'
                             'Phone: (555) 123-4567')
    
    def reset_password(self):
        # Show password reset dialog
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, 'Password Reset', 
                             'Please enter your username first')
            self.username_input.setFocus()
            return
            
        QMessageBox.information(self, 'Password Reset', 
                             f'A password reset link will be sent to the email\n'
                             f'associated with username: {username}')
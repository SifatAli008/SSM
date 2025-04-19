# Application settings
APP_NAME = "Smart Shop Manager"
APP_VERSION = "1.0.0"

# UI Settings
UI_THEME = "default"
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

# Firebase Collections
COLLECTION_USERS = "users"
COLLECTION_CUSTOMERS = "customers"
COLLECTION_INVENTORY = "inventory"
COLLECTION_SALES = "sales"
COLLECTION_SUPPLIERS = "suppliers"

# Role definitions
ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"  # New role for store managers
ROLE_CASHIER = "cashier"  # New role for cashiers
ROLE_STAFF = "staff"      # Kept for backward compatibility

# Role access levels (higher number = more access)
ROLE_ACCESS = {
    ROLE_ADMIN: 100,
    ROLE_MANAGER: 75, 
    ROLE_STAFF: 50,
    ROLE_CASHIER: 25
}

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "adminPass123"
DEFAULT_ADMIN_FULL_NAME = "Admin User"  # Ensure this exists

# Default credentials for demonstration
DEFAULT_MANAGER_USERNAME = "manager"
DEFAULT_MANAGER_PASSWORD = "managerPass123"

DEFAULT_CASHIER_USERNAME = "cashier"
DEFAULT_CASHIER_PASSWORD = "cashierPass123"

# Backup Settings
BACKUP_INTERVAL_DAYS = 1
LOCAL_BACKUP_PATH = "backups/"

# Report Settings
REPORT_OUTPUT_PATH = "reports/"

# UI Theme colors
UI_COLORS = {
    "primary": "#3498db",
    "secondary": "#2ecc71",
    "accent": "#9b59b6",
    "background": "#f5f5f5",
    "error": "#e74c3c",
    "text_primary": "#333333",
    "text_secondary": "#777777"
}

# Feature access control based on roles
FEATURE_ACCESS = {
    "inventory_management": [ROLE_ADMIN, ROLE_MANAGER, ROLE_STAFF],
    "user_management": [ROLE_ADMIN],
    "reports": [ROLE_ADMIN, ROLE_MANAGER],
    "sales": [ROLE_ADMIN, ROLE_MANAGER, ROLE_STAFF, ROLE_CASHIER],
    "suppliers": [ROLE_ADMIN, ROLE_MANAGER],
    "settings": [ROLE_ADMIN],
    "backup": [ROLE_ADMIN]
}
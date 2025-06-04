import pytest
import os
import shutil
from pathlib import Path
import sqlite3
import tempfile
from datetime import datetime
import json

from app.utils.config_manager import ConfigManager
from app.utils.database import DatabaseManager
from app.utils.auth import AuthManager
from app.utils.backup import BackupManager
from app.utils.error_handler import ErrorHandler

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="session")
def test_config(temp_dir):
    """Create a test configuration."""
    config = {
        "app": {
            "name": "Smart Shop Manager Test",
            "version": "1.0.0",
            "debug": True
        },
        "database": {
            "type": "sqlite",
            "path": os.path.join(temp_dir, "test.db"),
            "backup_interval_hours": 1
        },
        "security": {
            "min_password_length": 8,
            "require_special_chars": True,
            "session_timeout_minutes": 30,
            "max_login_attempts": 3
        },
        "logging": {
            "level": "DEBUG",
            "file": os.path.join(temp_dir, "test.log"),
            "max_size": 1024 * 1024,  # 1MB
            "backup_count": 2,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "backup": {
            "max_backups": 3,
            "backup_interval_hours": 1,
            "include_files": ["data/*", "config/*"],
            "exclude_files": ["*.log", "*.tmp"]
        }
    }
    
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    return config

@pytest.fixture(scope="session")
def test_db(temp_dir):
    """Create a test database."""
    db_path = os.path.join(temp_dir, "test.db")
    
    # Create test database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create test tables
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
    ''')
    
    # Insert test data
    cursor.executescript('''
        INSERT INTO users (username, password_hash, role) VALUES
        ('test_admin', 'hashed_password', 'admin'),
        ('test_user', 'hashed_password', 'user');
        
        INSERT INTO products (name, description, price, stock) VALUES
        ('Test Product 1', 'Description 1', 10.99, 100),
        ('Test Product 2', 'Description 2', 20.99, 50);
    ''')
    
    conn.commit()
    conn.close()
    
    return db_path

@pytest.fixture(scope="function")
def db_connection(test_db):
    """Create a database connection for each test."""
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()

@pytest.fixture(scope="function")
def config_manager(test_config, temp_dir):
    """Create a test configuration manager."""
    manager = ConfigManager()
    manager.config = test_config
    return manager

@pytest.fixture(scope="function")
def auth_manager():
    """Create a test authentication manager."""
    return AuthManager()

@pytest.fixture(scope="function")
def backup_manager(test_db):
    """Create a test backup manager."""
    return BackupManager(test_db)

@pytest.fixture(scope="function")
def error_handler():
    """Create a test error handler."""
    return ErrorHandler()

@pytest.fixture(scope="function")
def test_user():
    """Create test user data."""
    return {
        "username": "test_user",
        "password": "TestPass123!",
        "role": "user"
    }

@pytest.fixture(scope="function")
def test_admin():
    """Create test admin data."""
    return {
        "username": "test_admin",
        "password": "AdminPass123!",
        "role": "admin"
    }

@pytest.fixture(scope="function")
def test_product():
    """Create test product data."""
    return {
        "name": "Test Product",
        "description": "Test Description",
        "price": 19.99,
        "stock": 100
    }

@pytest.fixture(scope="function")
def test_sale():
    """Create test sale data."""
    return {
        "product_id": 1,
        "quantity": 5,
        "total_price": 99.95
    }

def pytest_configure(config):
    """Configure pytest."""
    # Add custom markers
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers",
        "security: mark test as security related"
    ) 
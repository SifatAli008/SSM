import pytest
import sqlite3
from datetime import datetime
from app.utils.database import DatabaseManager
from app.utils.error_handler import DatabaseError

@pytest.mark.integration
class TestDatabaseManager:
    def test_database_connection(self, db_connection):
        """Test database connection and basic operations."""
        cursor = db_connection.cursor()
        
        # Test connection is working
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        
        # Test connection attributes
        assert db_connection.isolation_level is not None
        assert db_connection.row_factory is not None
    
    def test_user_operations(self, db_connection):
        """Test user-related database operations."""
        cursor = db_connection.cursor()
        
        # Test user creation
        cursor.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        """, ("test_user_new", "hashed_password", "user"))
        db_connection.commit()
        
        # Test user retrieval
        cursor.execute("SELECT * FROM users WHERE username = ?", ("test_user_new",))
        user = cursor.fetchone()
        assert user is not None
        assert user[1] == "test_user_new"
        assert user[3] == "user"
        
        # Test user update
        cursor.execute("""
            UPDATE users 
            SET role = ? 
            WHERE username = ?
        """, ("admin", "test_user_new"))
        db_connection.commit()
        
        cursor.execute("SELECT role FROM users WHERE username = ?", ("test_user_new",))
        updated_role = cursor.fetchone()[0]
        assert updated_role == "admin"
        
        # Test user deletion
        cursor.execute("DELETE FROM users WHERE username = ?", ("test_user_new",))
        db_connection.commit()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", ("test_user_new",))
        deleted_user = cursor.fetchone()
        assert deleted_user is None
    
    def test_product_operations(self, db_connection):
        """Test product-related database operations."""
        cursor = db_connection.cursor()
        
        # Test product creation
        cursor.execute("""
            INSERT INTO products (name, description, price, stock)
            VALUES (?, ?, ?, ?)
        """, ("Test Product New", "Test Description", 29.99, 50))
        db_connection.commit()
        
        # Test product retrieval
        cursor.execute("SELECT * FROM products WHERE name = ?", ("Test Product New",))
        product = cursor.fetchone()
        assert product is not None
        assert product[1] == "Test Product New"
        assert product[3] == 29.99
        assert product[4] == 50
        
        # Test product update
        cursor.execute("""
            UPDATE products 
            SET price = ?, stock = ? 
            WHERE name = ?
        """, (39.99, 75, "Test Product New"))
        db_connection.commit()
        
        cursor.execute("SELECT price, stock FROM products WHERE name = ?", ("Test Product New",))
        updated_product = cursor.fetchone()
        assert updated_product[0] == 39.99
        assert updated_product[1] == 75
        
        # Test product deletion
        cursor.execute("DELETE FROM products WHERE name = ?", ("Test Product New",))
        db_connection.commit()
        
        cursor.execute("SELECT * FROM products WHERE name = ?", ("Test Product New",))
        deleted_product = cursor.fetchone()
        assert deleted_product is None
    
    def test_sale_operations(self, db_connection):
        """Test sale-related database operations."""
        cursor = db_connection.cursor()
        
        # Test sale creation
        cursor.execute("""
            INSERT INTO sales (product_id, quantity, total_price)
            VALUES (?, ?, ?)
        """, (1, 5, 54.95))
        db_connection.commit()
        
        # Test sale retrieval
        cursor.execute("SELECT * FROM sales WHERE product_id = ?", (1,))
        sale = cursor.fetchone()
        assert sale is not None
        assert sale[1] == 1  # product_id
        assert sale[2] == 5  # quantity
        assert sale[3] == 54.95  # total_price
        
        # Test sale update
        cursor.execute("""
            UPDATE sales 
            SET quantity = ?, total_price = ? 
            WHERE product_id = ? AND quantity = ?
        """, (10, 109.90, 1, 5))
        db_connection.commit()
        
        cursor.execute("SELECT quantity, total_price FROM sales WHERE product_id = ?", (1,))
        updated_sale = cursor.fetchone()
        assert updated_sale[0] == 10
        assert updated_sale[1] == 109.90
        
        # Test sale deletion
        cursor.execute("DELETE FROM sales WHERE product_id = ? AND quantity = ?", (1, 10))
        db_connection.commit()
        
        cursor.execute("SELECT * FROM sales WHERE product_id = ? AND quantity = ?", (1, 10))
        deleted_sale = cursor.fetchone()
        assert deleted_sale is None
    
    def test_foreign_key_constraints(self, db_connection):
        """Test foreign key constraints."""
        cursor = db_connection.cursor()
        
        # Test invalid product_id in sales
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO sales (product_id, quantity, total_price)
                VALUES (?, ?, ?)
            """, (999, 1, 10.99))
            db_connection.commit()
    
    def test_transaction_rollback(self, db_connection):
        """Test transaction rollback functionality."""
        cursor = db_connection.cursor()
        
        # Start transaction
        db_connection.execute("BEGIN TRANSACTION")
        
        try:
            # Perform operations
            cursor.execute("""
                INSERT INTO products (name, description, price, stock)
                VALUES (?, ?, ?, ?)
            """, ("Test Product Rollback", "Test Description", 19.99, 100))
            
            # Force an error
            cursor.execute("SELECT * FROM nonexistent_table")
            
        except sqlite3.OperationalError:
            # Rollback on error
            db_connection.rollback()
        
        # Verify rollback
        cursor.execute("SELECT * FROM products WHERE name = ?", ("Test Product Rollback",))
        product = cursor.fetchone()
        assert product is None
    
    def test_database_backup(self, db_connection):
        """Test database backup functionality."""
        cursor = db_connection.cursor()
        
        # Create backup connection
        backup_conn = sqlite3.connect(":memory:")
        
        # Perform backup
        db_connection.backup(backup_conn)
        
        # Verify backup
        backup_cursor = backup_conn.cursor()
        backup_cursor.execute("SELECT COUNT(*) FROM users")
        user_count = backup_cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        original_user_count = cursor.fetchone()[0]
        
        assert user_count == original_user_count
        
        backup_conn.close()
    
    def test_database_integrity(self, db_connection):
        """Test database integrity checks."""
        cursor = db_connection.cursor()
        
        # Check foreign key constraints
        cursor.execute("PRAGMA foreign_key_check")
        assert cursor.fetchone() is None
        
        # Check database integrity
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        assert result[0] == "ok"
    
    def test_database_performance(self, db_connection):
        """Test database performance with bulk operations."""
        cursor = db_connection.cursor()
        
        # Test bulk insert
        products = [
            (f"Bulk Product {i}", f"Description {i}", 10.99 + i, 100)
            for i in range(100)
        ]
        
        cursor.executemany("""
            INSERT INTO products (name, description, price, stock)
            VALUES (?, ?, ?, ?)
        """, products)
        db_connection.commit()
        
        # Verify bulk insert
        cursor.execute("SELECT COUNT(*) FROM products WHERE name LIKE 'Bulk Product%'")
        count = cursor.fetchone()[0]
        assert count == 100
        
        # Clean up
        cursor.execute("DELETE FROM products WHERE name LIKE 'Bulk Product%'")
        db_connection.commit() 
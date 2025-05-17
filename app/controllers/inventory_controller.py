from PyQt5.QtSql import QSqlTableModel, QSqlQuery
from PyQt5.QtCore import Qt
import os
import csv
import datetime
from app.utils.database import DatabaseManager
from app.utils.logger import logger
from app.utils.event_system import global_event_system
from app.utils.cache_manager import global_cache

class InventoryController:
    def __init__(self):
        # Setup database connection using DatabaseManager
        self.db = DatabaseManager.get_qt_connection()
        
        if not self.db or not self.db.isOpen():
            logger.error("Failed to open database connection in InventoryController")
            return
            
        # Create tables if they don't exist
        self._create_tables()
        logger.info("Inventory controller initialized with database connection")

        # Initialize the model for the inventory table
        self.model = QSqlTableModel(db=self.db)
        self.model.setTable("inventory")
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.select()

        # Set column headers
        headers = ["ID", "Item Name", "Details", "Category", "Stock", "Buying Price", "Selling Price", "Last Updated"]
        for i, header in enumerate(headers):
            self.model.setHeaderData(i, Qt.Horizontal, header)

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        query = QSqlQuery(self.db)
        
        # Create inventory table
        create_inventory_table = """
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            details TEXT,
            category TEXT DEFAULT 'Other',
            stock INTEGER DEFAULT 0,
            buying_price REAL DEFAULT 0.0,
            selling_price REAL DEFAULT 0.0,
            last_updated TEXT
        )
        """
        
        if not query.exec_(create_inventory_table):
            print(f"❌ Error creating inventory table: {query.lastError().text()}")
            
        # Create sales table for future use
        create_sales_table = """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_id INTEGER,
            quantity INTEGER,
            sale_price REAL,
            sale_date TEXT,
            FOREIGN KEY (inventory_id) REFERENCES inventory (id)
        )
        """
        
        if not query.exec_(create_sales_table):
            print(f"❌ Error creating sales table: {query.lastError().text()}")

    def add_product(self, name, quantity, buying_price, selling_price=None, details="", category="Other"):
        """Adds a new product to the inventory."""
        try:
            # If selling price is not provided, set it to buying price + 20%
            if selling_price is None:
                selling_price = buying_price * 1.2
                
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert a new row
            row = self.model.rowCount()
            self.model.insertRow(row)
            
            # Set data for each column
            self.model.setData(self.model.index(row, 1), name)
            self.model.setData(self.model.index(row, 2), details)
            self.model.setData(self.model.index(row, 3), category)
            self.model.setData(self.model.index(row, 4), int(quantity))
            self.model.setData(self.model.index(row, 5), float(buying_price))
            self.model.setData(self.model.index(row, 6), float(selling_price))
            self.model.setData(self.model.index(row, 7), current_datetime)

            if self.model.submitAll():
                print(f"✅ Product '{name}' added successfully.")
                
                # Clear relevant caches when inventory changes
                self._invalidate_caches()
                
                # Notify the event system about the change with product data
                event_data = {
                    "action": "add",
                    "product": {
                        "name": name,
                        "quantity": quantity,
                        "buying_price": buying_price,
                        "selling_price": selling_price,
                        "category": category
                    }
                }
                global_event_system.notify_inventory_update(event_data)
                return True
            else:
                print(f"❌ Failed to submit new product: {self.model.lastError().text()}")
                return False
        except Exception as e:
            print(f"❌ Error in add_product: {e}")
            return False

    def delete_item(self, row):
        """Deletes an item by row index."""
        try:
            # Get item data for event notification
            item_id = self.model.data(self.model.index(row, 0))
            item_name = self.model.data(self.model.index(row, 1))
            item_category = self.model.data(self.model.index(row, 3))
            
            # Remove the row
            success = self.model.removeRow(row)
            if success and self.model.submitAll():
                print(f"🗑️ Product '{item_name}' deleted successfully.")
                
                # Clear relevant caches when inventory changes
                self._invalidate_caches()
                
                # Notify the event system about the change with product data
                event_data = {
                    "action": "delete",
                    "product": {
                        "id": item_id,
                        "name": item_name,
                        "category": item_category
                    }
                }
                global_event_system.notify_inventory_update(event_data)
                return True
            else:
                print(f"❌ Error deleting product: {self.model.lastError().text()}")
                return False
        except Exception as e:
            print(f"❌ Error in delete_item: {e}")
            return False

    def delete_multiple_items(self, rows):
        """Deletes multiple items by row indices."""
        deleted_count = 0
        for row in sorted(rows, reverse=True):  # Delete in reverse order to avoid index shifting
            if self.delete_item(row):
                deleted_count += 1
        
        # Notify the event system about the change if any items were deleted
        if deleted_count > 0:
            global_event_system.notify_inventory_update()
            
        return deleted_count

    def update_item(self, row, data, additional_data=None):
        """Updates an existing item at the specified row."""
        try:
            # Get item ID and name for event notification
            item_id = self.model.data(self.model.index(row, 0))
            item_name = self.model.data(self.model.index(row, 1))
            
            # Update each field
            for column, value in data.items():
                self.model.setData(self.model.index(row, column), value)
            
            # Update additional fields if provided
            if additional_data:
                if 'details' in additional_data:
                    self.model.setData(self.model.index(row, 2), additional_data['details'])
                if 'category' in additional_data:
                    self.model.setData(self.model.index(row, 3), additional_data['category'])
            
            # Add last updated timestamp
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.model.setData(self.model.index(row, 7), current_datetime)
            
            # Submit changes
            if self.model.submitAll():
                print(f"✅ Product '{item_name}' updated successfully.")
                
                # Clear relevant caches when inventory changes
                self._invalidate_caches()
                
                # Prepare event data with updated values
                event_data = {
                    "action": "update",
                    "product": {
                        "id": item_id,
                        "name": item_name,
                    }
                }
                
                # Add updated data to event payload
                for column, value in data.items():
                    if column == 1:
                        event_data["product"]["name"] = value
                    elif column == 4:
                        event_data["product"]["quantity"] = value
                
                # Add additional data if available
                if additional_data:
                    for key, value in additional_data.items():
                        event_data["product"][key] = value
                
                # Notify the event system about the change
                global_event_system.notify_inventory_update(event_data)
                return True
            else:
                print(f"❌ Error updating product: {self.model.lastError().text()}")
                return False
        except Exception as e:
            print(f"❌ Error in update_item: {e}")
            return False

    def refresh_data(self):
        """Refreshes the data from the database."""
        try:
            self.model.select()
            # Clear all inventory caches when refreshing data
            self._invalidate_caches()
            print("🔄 Data refreshed.")
            return True
        except Exception as e:
            print(f"❌ Error refreshing data: {e}")
            return False

    def count_total_stock(self):
        """Counts the total stock across all inventory items."""
        # Try to get from cache first
        cache_key = "inventory:total_stock"
        cached_value = global_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
            
        # If not in cache, calculate from database
        total = 0
        for row in range(self.model.rowCount()):
            stock = self.model.data(self.model.index(row, 4))
            if stock:
                try:
                    total += int(stock)
                except ValueError:
                    print(f"⚠️ Skipping invalid stock value at row {row}: {stock}")
        
        # Store in cache for 5 minutes
        global_cache.set(cache_key, total, ttl_seconds=300)
        return total

    def count_low_stock(self, threshold=10):
        """Counts items with stock below the specified threshold."""
        # Try to get from cache first
        cache_key = f"inventory:low_stock:{threshold}"
        cached_value = global_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
            
        # If not in cache, calculate from database
        low = 0
        for row in range(self.model.rowCount()):
            stock = self.model.data(self.model.index(row, 4))
            if stock:
                try:
                    if int(stock) < threshold:
                        low += 1
                except ValueError:
                    print(f"⚠️ Invalid stock at row {row}: {stock}")
        
        # Store in cache for 5 minutes
        global_cache.set(cache_key, low, ttl_seconds=300)
        return low

    def count_medium_stock(self, min_threshold=11, max_threshold=50):
        """Counts items with stock between the specified thresholds."""
        # Try to get from cache first
        cache_key = f"inventory:medium_stock:{min_threshold}_{max_threshold}"
        cached_value = global_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
            
        # If not in cache, calculate from database
        medium = 0
        for row in range(self.model.rowCount()):
            stock = self.model.data(self.model.index(row, 4))
            if stock:
                try:
                    stock_value = int(stock)
                    if min_threshold <= stock_value <= max_threshold:
                        medium += 1
                except ValueError:
                    print(f"⚠️ Invalid stock at row {row}: {stock}")
        
        # Store in cache for 5 minutes
        global_cache.set(cache_key, medium, ttl_seconds=300)
        return medium

    def count_high_stock(self, threshold=50):
        """Counts items with stock above the specified threshold."""
        # Try to get from cache first
        cache_key = f"inventory:high_stock:{threshold}"
        cached_value = global_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
            
        # If not in cache, calculate from database
        high = 0
        for row in range(self.model.rowCount()):
            stock = self.model.data(self.model.index(row, 4))
            if stock:
                try:
                    if int(stock) > threshold:
                        high += 1
                except ValueError:
                    print(f"⚠️ Invalid stock at row {row}: {stock}")
        
        # Store in cache for 5 minutes
        global_cache.set(cache_key, high, ttl_seconds=300)
        return high

    def get_low_stock_items(self, threshold=10):
        """Returns a list of items with stock below the specified threshold."""
        # Try to get from cache first
        cache_key = f"inventory:low_stock_items:{threshold}"
        cached_value = global_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
            
        # If not in cache, calculate from database
        low_stock_items = []
        for row in range(self.model.rowCount()):
            item_id = self.model.data(self.model.index(row, 0))
            name = self.model.data(self.model.index(row, 1))
            stock = self.model.data(self.model.index(row, 4))
            category = self.model.data(self.model.index(row, 3))
            
            if stock:
                try:
                    stock_value = int(stock)
                    if stock_value < threshold:
                        low_stock_items.append({
                            'id': item_id,
                            'name': name,
                            'stock': stock_value,
                            'category': category
                        })
                except ValueError:
                    print(f"⚠️ Invalid stock at row {row}: {stock}")
        
        # Store in cache for 5 minutes
        global_cache.set(cache_key, low_stock_items, ttl_seconds=300)
        return low_stock_items

    def count_recent_items(self, days=7):
        """Counts items added or updated in the last X days."""
        count = 0
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
        
        for row in range(self.model.rowCount()):
            last_updated = self.model.data(self.model.index(row, 7))
            if last_updated and last_updated > cutoff_str:
                count += 1
        return count

    def calculate_inventory_value(self):
        """Calculates the total value of inventory."""
        # Try to get from cache first
        cache_key = "inventory:total_value"
        cached_value = global_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
            
        # If not in cache, calculate from database
        total_value = 0
        for row in range(self.model.rowCount()):
            stock = self.model.data(self.model.index(row, 4))
            buying_price = self.model.data(self.model.index(row, 5))
            if stock and buying_price:
                try:
                    total_value += int(stock) * float(buying_price)
                except (ValueError, TypeError):
                    continue
        
        # Store in cache for 5 minutes
        global_cache.set(cache_key, total_value, ttl_seconds=300)
        return total_value

    def get_product_details(self, row):
        """Gets the product details for a specific row."""
        return self.model.data(self.model.index(row, 2))

    def get_product_category(self, row):
        """Gets the product category for a specific row."""
        return self.model.data(self.model.index(row, 3))

    def upload_bulk_stock(self, filepath):
        """Uploads bulk stock data from a CSV file."""
        success_count = 0
        error_count = 0
        
        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        name = row.get('Item Name', '').strip()
                        details = row.get('Details', '').strip()
                        category = row.get('Category', 'Other').strip()
                        stock = int(row.get('Stock', '0').strip())
                        buying_price = float(row.get('Buying Price', '0').strip())
                        selling_price = float(row.get('Selling Price', '0').strip())
                        
                        if self.add_product(name, stock, buying_price, selling_price, details, category):
                            success_count += 1
                        else:
                            error_count += 1
                            
                    except (ValueError, KeyError) as e:
                        print(f"⚠️ Error processing row: {row} - {str(e)}")
                        error_count += 1
                        
            print(f"✅ Bulk upload completed. Success: {success_count}, Errors: {error_count}")
            return True, success_count, error_count
        except Exception as e:
            print(f"❌ Error uploading bulk stock: {e}")
            return False, 0, 0

    def export_inventory_to_csv(self, filepath):
        """Exports inventory data to a CSV file."""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                headers = ["Item Name", "Details", "Category", "Stock", "Buying Price", "Selling Price", "Last Updated"]
                writer.writerow(headers)
                
                # Write data
                count = 0
                for row in range(self.model.rowCount()):
                    data = []
                    for col in range(1, 8):  # Skip ID column
                        data.append(self.model.data(self.model.index(row, col)))
                    writer.writerow(data)
                    count += 1
                    
            print(f"✅ Exported {count} items to CSV successfully.")
            return True, count
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False, 0

    def search_products(self, query):
        """Search for products by name."""
        self.model.setFilter(f"name LIKE '%{query}%'")
        self.model.select()

    def get_all_categories(self):
        """Get all unique categories from the inventory."""
        # Try to get from cache first
        cache_key = "inventory:categories"
        cached_value = global_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
            
        # If not in cache, get from database
        categories = set()
        for row in range(self.model.rowCount()):
            category = self.model.data(self.model.index(row, 3))
            if category:
                categories.add(category)
        
        result = sorted(list(categories)) or ["Electronics", "Food", "Clothing", "Other"]
        
        # Store in cache for 10 minutes (categories change less frequently)
        global_cache.set(cache_key, result, ttl_seconds=600)
        return result
    
    def delete_category(self, category_name):
        """
        Delete a category by updating all products in that category to 'Other'.
        
        Args:
            category_name (str): The name of the category to delete
            
        Returns:
            tuple: (success, count) where count is the number of products updated
        """
        try:
            count = 0
            # Create a raw SQL query for direct execution
            query = QSqlQuery(self.db)
            
            # First count products in this category for reporting
            count_query = f"SELECT COUNT(*) FROM inventory WHERE category = '{category_name}'"
            if query.exec_(count_query) and query.next():
                count = query.value(0)
            
            # Now update all products with this category to 'Other'
            update_query = f"UPDATE inventory SET category = 'Other' WHERE category = '{category_name}'"
            
            if query.exec_(update_query):
                print(f"✅ Category '{category_name}' deleted, {count} products updated to 'Other'.")
                # Refresh the model to reflect changes
                self.model.select()
                # Notify the event system about the change
                global_event_system.notify_inventory_update()
                return True, count
            else:
                print(f"❌ Error deleting category: {query.lastError().text()}")
                return False, 0
        except Exception as e:
            print(f"❌ Error in delete_category: {e}")
            return False, 0

    def close_database(self):
        """Closes the database connection."""
        if self.db.isOpen():
            self.db.close()
            print("✅ Database connection closed.")

    def _invalidate_caches(self):
        """Invalidate all inventory-related caches when data changes"""
        global_cache.delete("inventory:total_stock")
        global_cache.delete("inventory:total_value")
        global_cache.delete("inventory:categories")
        
        # Delete low stock caches with different thresholds
        for i in range(1, 21):  # Common threshold values
            global_cache.delete(f"inventory:low_stock:{i}")
            global_cache.delete(f"inventory:low_stock_items:{i}")
            global_cache.delete(f"inventory:high_stock:{i*5}")  # Common high stock thresholds
            
        # Delete medium stock caches with common threshold ranges
        common_ranges = [(1, 10), (5, 20), (10, 50), (11, 50), (10, 100)]
        for min_val, max_val in common_ranges:
            global_cache.delete(f"inventory:medium_stock:{min_val}_{max_val}")
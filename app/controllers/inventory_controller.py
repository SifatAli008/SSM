from PyQt5.QtSql import QSqlTableModel, QSqlQuery
from PyQt5.QtCore import Qt
import os
import csv
import datetime
from app.utils.database import DatabaseManager
from app.utils.logger import Logger
logger = Logger()
from app.utils.event_system import global_event_system
from app.utils.cache_manager import global_cache
from app.models.inventory import FirebaseInventoryTableModel
from app.core.inventory import InventoryManager
import attr
from app.data.data_provider import BaseDataProvider

@attr.s(auto_attribs=True)
class Product:
    name: str = ''
    quantity: int = 0
    price: float = 0.0
    category: str = ''
    details: str = ''
    buying_price: float = 0.0
    selling_price: float = 0.0
    stock: int = 0
    id: int = 0

class InventoryController:
    def __init__(self, data_provider: BaseDataProvider, event_system=None):
        self.data_provider = data_provider
        self.manager = InventoryManager(event_system)
        self.model = FirebaseInventoryTableModel(event_system)
        self.db = None
        self.products = []

    def refresh_data(self):
        self.model.refresh()

    def add_product(self, *args, **kwargs):
        if args:
            raise ValueError("add_product only accepts named arguments (use name=..., quantity=..., etc.)")
        name = kwargs.get('name', '').strip()
        if not name:
            logger.error("Product name is required and cannot be empty.")
            raise ValueError("Product name is required.")
        # Check for duplicate
        if self.get_product(name):
            logger.error(f"Duplicate product: {name}")
            return False
        # Ensure 'quantity' and 'stock' are both set
        quantity = kwargs.get('quantity', 0)
        price = kwargs.get('price', 0)
        if quantity < 0 or price < 0:
            logger.error(f"Invalid product data: negative quantity or price (quantity={quantity}, price={price})")
            return False
        if 'quantity' in kwargs:
            kwargs['stock'] = kwargs.get('stock', kwargs['quantity'])
        elif 'stock' in kwargs:
            kwargs['quantity'] = kwargs.get('quantity', kwargs['stock'])
        logger.info(f"Adding product with values: {kwargs}")
        product_data = {k: kwargs.get(k, getattr(Product, k, '')) for k in Product.__annotations__.keys()}
        try:
            prod_id = self.data_provider.add_product(product_data)
            return prod_id
        except Exception as e:
            logger.error(f"Data provider error on add_product: {e}")
            return False

    def get_all_products(self):
        return self.data_provider.get_products()

    def get_product(self, name):
        products = self.data_provider.get_products()
        for prod in products:
            if prod.get('name') == name:
                return prod
        return None

    def delete_product(self, name):
        # Remove product from mock data provider (list of dicts)
        for prod in self.data_provider.products:
            if prod.get('name') == name:
                self.data_provider.products.remove(prod)
                return True
        return False

    def update_product(self, name, **kwargs):
        # Update product in mock data provider (list of dicts)
        for prod in self.data_provider.products:
            if prod.get('name') == name:
                prod.update(kwargs)
                return True
        return False

    def delete_item(self, row):
        try:
            # Get product data before deletion for event
            product_id = self.model.data(self.model.index(row, 0))
            product_name = self.model.data(self.model.index(row, 1))
            result = self.model.removeRow(row)
            self.refresh_data()
            # Emit inventory update event for real-time sync
            if result:
                global_event_system.notify_inventory_update({"action": "delete", "product": {"id": product_id, "name": product_name}})
            return result
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False

    def update_item(self, row, updated_data, additional_data=None):
        try:
            for col, value in updated_data.items():
                idx = self.model.index(row, col)
                self.model.setData(idx, value, Qt.EditRole)
            if additional_data:
                for key, value in additional_data.items():
                    # Map additional fields to columns if needed
                    if key == "details":
                        idx = self.model.index(row, 2)
                        self.model.setData(idx, value, Qt.EditRole)
                    elif key == "category":
                        idx = self.model.index(row, 3)
                        self.model.setData(idx, value, Qt.EditRole)
                    elif key == "buying_price":
                        idx = self.model.index(row, 5)
                        self.model.setData(idx, value, Qt.EditRole)
                    elif key == "selling_price":
                        idx = self.model.index(row, 6)
                        self.model.setData(idx, value, Qt.EditRole)
            self.refresh_data()
            # Emit inventory update event for real-time sync
            global_event_system.notify_inventory_update({"action": "update", "product": updated_data})
            return True
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            return False

    def insert_item(self, row, item_data):
        try:
            result = self.model.insertRow(row, item_data=item_data)
            self.refresh_data()
            # Emit inventory update event for real-time sync
            if result:
                global_event_system.notify_inventory_update({"action": "add", "product": item_data})
            return result
        except Exception as e:
            logger.error(f"Error inserting product: {e}")
            return False

    def count_total_stock(self):
        try:
            products = self.manager.list_products()
            return sum((getattr(p, 'quantity', getattr(p, 'stock', 0)) or 0) for p in products)
        except Exception as e:
            logger.error(f"Error counting total stock: {e}")
            return 0

    def count_low_stock(self, threshold=10):
        try:
            products = self.manager.list_products()
            return sum(1 for p in products if (getattr(p, 'quantity', getattr(p, 'stock', 0)) or 0) < threshold)
        except Exception as e:
            logger.error(f"Error counting low stock: {e}")
            return 0

    def count_recent_items(self, days=7):
        from datetime import datetime, timedelta
        try:
            products = self.manager.list_products()
            cutoff = datetime.now() - timedelta(days=days)
            count = 0
            for p in products:
                updated = getattr(p, 'updated_at', None)
                if updated and isinstance(updated, str):
                    try:
                        updated = datetime.fromisoformat(updated)
                    except Exception:
                        continue
                if updated and updated > cutoff:
                    count += 1
            return count
        except Exception as e:
            logger.error(f"Error counting recent items: {e}")
            return 0

    def calculate_inventory_value(self):
        try:
            products = self.manager.list_products()
            return sum((getattr(p, 'quantity', getattr(p, 'stock', 0)) or 0) * (getattr(p, 'buying_price', getattr(p, 'cost_price', 0.0)) or 0.0) for p in products)
        except Exception as e:
            logger.error(f"Error calculating inventory value: {e}")
            return 0.0

    def get_all_categories(self):
        try:
            products = self.manager.list_products()
            categories = set(getattr(p, 'category', 'Other') for p in products)
            return sorted(categories | {"Electronics", "Food", "Clothing", "Other"})
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return ["Electronics", "Food", "Clothing", "Other"]

    def delete_category(self, category_name):
        try:
            products = self.manager.list_products()
            count = 0
            for p in products:
                if getattr(p, 'category', 'Other') == category_name:
                    self.manager.update_product(getattr(p, 'id', getattr(p, 'item_id', None)), {"category": "Other"})
                    count += 1
            self.refresh_data()
            return True, count
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return False, 0

    def export_inventory_to_csv(self, filepath):
        import csv
        try:
            products = self.manager.list_products()
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                headers = ["ID", "Product Name", "Product Details", "Category", "Quantity", "Buying Price", "Selling Price"]
                writer.writerow(headers)
                count = 0
                for p in products:
                    quantity = getattr(p, 'quantity', getattr(p, 'stock', 0))
                    try:
                        quantity = int(quantity) if quantity not in (None, "") else 0
                    except (ValueError, TypeError):
                        quantity = 0
                    row = [
                        getattr(p, 'id', getattr(p, 'item_id', '')),
                        getattr(p, 'name', ''),
                        getattr(p, 'details', getattr(p, 'description', '')),
                        getattr(p, 'category', 'Other'),
                        quantity,
                        getattr(p, 'buying_price', getattr(p, 'cost_price', 0.0)),
                        getattr(p, 'selling_price', 0.0)
                    ]
                    writer.writerow(row)
                    count += 1
            return True, count
        except Exception as e:
            logger.error(f"Error exporting inventory to CSV: {e}")
            return False, 0

    def search_products(self, query):
        """Search for products by name."""
        self.model.setFilter(f"name LIKE '%{query}%'")
        self.model.select()

    def count_medium_stock(self, min_threshold=11, max_threshold=50):
        """Counts items with stock between the specified thresholds."""
        cache_key = f"inventory:medium_stock:{min_threshold}_{max_threshold}"
        cached_value = global_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        medium = 0
        for row in range(self.model.rowCount()):
            stock = self.model.data(self.model.index(row, 4))
            try:
                stock_value = int(stock) if stock not in (None, "") else 0
                if min_threshold <= stock_value <= max_threshold:
                    medium += 1
            except (ValueError, TypeError):
                print(f"Warning: Invalid stock at row {row}: {stock}")
        global_cache.set(cache_key, medium, ttl_seconds=300)
        return medium

    def count_high_stock(self, threshold=50):
        """Counts items with stock above the specified threshold."""
        cache_key = f"inventory:high_stock:{threshold}"
        cached_value = global_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        high = 0
        for row in range(self.model.rowCount()):
            stock = self.model.data(self.model.index(row, 4))
            try:
                stock_value = int(stock) if stock not in (None, "") else 0
                if stock_value > threshold:
                    high += 1
            except (ValueError, TypeError):
                print(f"Warning: Invalid stock at row {row}: {stock}")
        global_cache.set(cache_key, high, ttl_seconds=300)
        return high

    def get_low_stock_items(self, threshold=10):
        """Returns a list of items with stock below the specified threshold."""
        cache_key = f"inventory:low_stock_items:{threshold}"
        cached_value = global_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        low_stock_items = []
        for row in range(self.model.rowCount()):
            item_id = self.model.data(self.model.index(row, 0))
            name = self.model.data(self.model.index(row, 1))
            stock = self.model.data(self.model.index(row, 4))
            category = self.model.data(self.model.index(row, 3))
            try:
                stock_value = int(stock) if stock not in (None, "") else 0
                if stock_value < threshold:
                    low_stock_items.append({
                        'id': item_id,
                        'name': name,
                        'stock': stock_value,
                        'category': category
                    })
            except (ValueError, TypeError):
                print(f"Warning: Invalid stock at row {row}: {stock}")
        global_cache.set(cache_key, low_stock_items, ttl_seconds=300)
        return low_stock_items

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
                        print(f"Warning: Error processing row: {row} - {str(e)}")
                        error_count += 1
                        
            print(f"Bulk upload completed. Success: {success_count}, Errors: {error_count}")
            return True, success_count, error_count
        except Exception as e:
            print(f"Error uploading bulk stock: {e}")
            return False, 0, 0

    def close_database(self):
        """Closes the database connection."""
        if self.db and self.db.isOpen():
            self.db.close()
            print("Database connection closed.")

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
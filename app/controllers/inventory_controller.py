from PyQt5.QtSql import QSqlTableModel, QSqlDatabase
from PyQt5.QtCore import Qt

class InventoryController:
    def __init__(self):
        # Attempt to connect to the local SQLite database
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('E:/UDH/smart_shop_manager/data/shop.db')  # Set correct path to your database

        if not self.db.open():
            print("Error: Database not open!")
            return
        
        print("✅ Database connection established successfully.")

        # Setup the model and configure it to interact with the 'inventory' table
        self.model = QSqlTableModel()
        self.model.setTable("inventory")
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.select()

        # Set headers for the inventory table
        headers = ["ID", "Item Name", "Stock", "Buying Price", "Selling Price"]
        for i, header in enumerate(headers):
            self.model.setHeaderData(i, Qt.Horizontal, header)

    def get_model(self):
        return self.model

    def add_item(self):
        try:
            row = self.model.rowCount()
            self.model.insertRow(row)
        except Exception as e:
            print(f"Error adding item: {e}")

    def delete_item(self, row):
        try:
            self.model.removeRow(row)
            self.model.submitAll()
        except Exception as e:
            print(f"Error deleting item: {e}")

    def refresh_data(self):
        try:
            self.model.select()
        except Exception as e:
            print(f"Error refreshing data: {e}")

    def update_item(self, row, data):
        try:
            for column, value in data.items():
                self.model.setData(self.model.index(row, column), value)
            self.model.submitAll()
        except Exception as e:
            print(f"Error updating item: {e}")

    def count_total_stock(self):
        count = 0
        for row in range(self.model.rowCount()):
            stock = self.model.data(self.model.index(row, 2))  # Stock column
            if stock:
                count += int(stock)
        return count

    def count_low_stock(self):
        low = 0
        for row in range(self.model.rowCount()):
            stock = self.model.data(self.model.index(row, 2))
            if stock and int(stock) < 10:
                low += 1
        return low

    def count_recent_items(self):
        return min(self.model.rowCount(), 12)

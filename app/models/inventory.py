from datetime import datetime
from config.database import FirebaseDB
from config.settings import COLLECTION_INVENTORY
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant
from app.core.inventory import InventoryManager

# --- Optionally keep InventoryItem for reference, but not as the main export ---
class InventoryItem:
    def __init__(self, name, quantity, cost_price, category="Test", id=None, price=None):
        self.name = name
        self.quantity = quantity
        self.cost_price = cost_price
        self.category = category
        self.id = id
        self.price = price if price is not None else cost_price
        
    def to_dict(self):
        """Convert InventoryItem object to dictionary for Firebase"""
        return {
            'name': self.name,
            'quantity': self.quantity,
            'cost_price': self.cost_price,
            'category': self.category,
            'id': self.id,
            'price': self.price
        }
        
    @staticmethod
    def from_dict(item_id, data):
        """Create InventoryItem object from Firebase document"""
        return InventoryItem(
            name=data.get('name'),
            quantity=data.get('quantity'),
            cost_price=data.get('cost_price'),
            category=data.get('category'),
            id=data.get('id'),
            price=data.get('price')
        )
    
    @staticmethod
    def get_all_items():
        """Get all inventory items from database"""
        db = FirebaseDB()
        items_ref = db.get_collection(COLLECTION_INVENTORY)
        items_docs = items_ref.stream()
        
        items = []
        for doc in items_docs:
            item = InventoryItem.from_dict(doc.id, doc.to_dict())
            items.append(item)
            
        return items
    
    @staticmethod
    def get_item_by_id(item_id):
        """Get item by ID"""
        db = FirebaseDB()
        items_ref = db.get_collection(COLLECTION_INVENTORY)
        item_doc = db.get_document(items_ref, item_id)
        
        if item_doc.exists:
            return InventoryItem.from_dict(item_id, item_doc.to_dict())
        return None
    
    @staticmethod
    def get_items_by_category(category):
        """Get items by category"""
        db = FirebaseDB()
        items_ref = db.get_collection(COLLECTION_INVENTORY)
        items = db.query_documents(items_ref, 'category', '==', category)
        
        result = []
        for item in items:
            result.append(InventoryItem.from_dict(item.id, item.to_dict()))
        return result
    
    @staticmethod
    def get_low_stock_items():
        """Get items that are below reorder level"""
        items = InventoryItem.get_all_items()
        return [item for item in items if item.quantity <= item.reorder_level]
    
    def save(self):
        """Save item to database"""
        db = FirebaseDB()
        items_ref = db.get_collection(COLLECTION_INVENTORY)
        
        self.updated_at = datetime.now()
        
        if self.id:
            # Update existing item
            db.update_document(items_ref, self.id, self.to_dict())
        else:
            # Create new item
            result = db.add_document(items_ref, self.to_dict())
            # If we're adding a new document, set the ID
            if hasattr(result, 'id'):
                self.id = result.id
        
        return self.id
    
    def update_quantity(self, new_quantity):
        """Update item quantity"""
        self.quantity = new_quantity
        self.updated_at = datetime.now()
        
        db = FirebaseDB()
        items_ref = db.get_collection(COLLECTION_INVENTORY)
        db.update_document(items_ref, self.id, {
            'quantity': self.quantity,
            'updated_at': self.updated_at
        })
        
    def delete(self):
        """Delete item from database"""
        if not self.id:
            return False
        
        db = FirebaseDB()
        items_ref = db.get_collection(COLLECTION_INVENTORY)
        db.delete_document(items_ref, self.id)
        return True

class FirebaseInventoryTableModel(QAbstractTableModel):
    headers = [
        "ID", "Product Name", "Product Details", "Category", "Quantity", "Buying Price", "Selling Price"
    ]

    def __init__(self, event_system=None, parent=None):
        super().__init__(parent)
        self.manager = InventoryManager(event_system)
        self.items = []  # List of dicts or objects
        self.item_ids = []  # Firebase keys
        self.load_data()

    def load_data(self):
        self.beginResetModel()
        products = self.manager.list_products()
        self.items = []
        self.item_ids = []
        for prod in products:
            # prod can be a dict or a Product object
            if hasattr(prod, 'dict'):
                data = prod.dict()
            elif hasattr(prod, '__dict__'):
                data = prod.__dict__
            else:
                data = dict(prod)
            self.items.append(data)
            self.item_ids.append(data.get('id') or data.get('item_id'))
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.items)):
            return QVariant()
        item = self.items[index.row()]
        col = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if col == 0:
                return self.item_ids[index.row()] or ""
            elif col == 1:
                return item.get("name", "")
            elif col == 2:
                return item.get("details", item.get("description", ""))
            elif col == 3:
                return item.get("category", "Other")
            elif col == 4:
                return item.get("quantity", item.get("stock", 0))
            elif col == 5:
                return item.get("buying_price", item.get("cost_price", 0.0))
            elif col == 6:
                return item.get("selling_price", 0.0)
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self.headers):
                return self.headers[section]
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False
        row = index.row()
        col = index.column()
        item_id = self.item_ids[row]
        item = self.items[row]
        key_map = {
            1: "name",
            2: "details",
            3: "category",
            4: "quantity",
            5: "buying_price",
            6: "selling_price"
        }
        if col in key_map:
            field = key_map[col]
            item[field] = value
            # Update in Firebase
            self.manager.update_product(item_id, {field: value})
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def insertRow(self, row, parent=QModelIndex(), item_data=None):
        self.beginInsertRows(QModelIndex(), row, row)
        prod_id = self.manager.create_product(item_data)
        if prod_id:
            item_data = dict(item_data)
            item_data['id'] = prod_id
            self.items.insert(row, item_data)
            self.item_ids.insert(row, prod_id)
            self.endInsertRows()
            return True
        self.endInsertRows()
        return False

    def removeRow(self, row, parent=QModelIndex()):
        if not (0 <= row < len(self.items)):
            return False
        self.beginRemoveRows(QModelIndex(), row, row)
        item_id = self.item_ids[row]
        self.manager.delete_product(item_id)
        del self.items[row]
        del self.item_ids[row]
        self.endRemoveRows()
        return True

    def refresh(self):
        self.load_data()

# --- Minimal Inventory class for test compatibility ---
class Inventory:
    def __init__(self, db=None):
        self.db = db
        self.items = []

    def create(self, name, quantity, price, category="Test"):
        item = InventoryItem(name=name, quantity=quantity, cost_price=price, category=category, id=len(self.items)+1, price=price)
        self.items.append(item)
        return item

    def get_by_name(self, name):
        for item in self.items:
            if item.name == name:
                return item
        return None

    def get_product(self, name):
        return self.get_by_name(name)

    def update(self, item_id, quantity=None, price=None):
        for item in self.items:
            if getattr(item, 'id', None) == item_id:
                if quantity is not None:
                    item.quantity = quantity
                if price is not None:
                    item.price = price
                return True
        return False
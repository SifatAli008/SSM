# ARCHIVED: Not used in current PyQt/SQLite inventory system.
'''
from datetime import datetime
from config.database import FirebaseDB
from config.settings import COLLECTION_INVENTORY

class InventoryItem:
    def __init__(self, item_id=None, name=None, description=None, category=None,
                quantity=0, cost_price=0.0, selling_price=0.0, 
                reorder_level=10, expiry_date=None, supplier_id=None):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.category = category
        self.quantity = quantity
        self.cost_price = cost_price
        self.selling_price = selling_price
        self.reorder_level = reorder_level
        self.expiry_date = expiry_date
        self.supplier_id = supplier_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def to_dict(self):
        """Convert InventoryItem object to dictionary for Firebase"""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'quantity': self.quantity,
            'cost_price': self.cost_price,
            'selling_price': self.selling_price,
            'reorder_level': self.reorder_level,
            'expiry_date': self.expiry_date,
            'supplier_id': self.supplier_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
    @staticmethod
    def from_dict(item_id, data):
        """Create InventoryItem object from Firebase document"""
        return InventoryItem(
            item_id=item_id,
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            quantity=data.get('quantity'),
            cost_price=data.get('cost_price'),
            selling_price=data.get('selling_price'),
            reorder_level=data.get('reorder_level'),
            expiry_date=data.get('expiry_date'),
            supplier_id=data.get('supplier_id')
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
        
        if self.item_id:
            # Update existing item
            db.update_document(items_ref, self.item_id, self.to_dict())
        else:
            # Create new item
            result = db.add_document(items_ref, self.to_dict())
            # If we're adding a new document, set the ID
            if hasattr(result, 'id'):
                self.item_id = result.id
        
        return self.item_id
    
    def update_quantity(self, new_quantity):
        """Update item quantity"""
        self.quantity = new_quantity
        self.updated_at = datetime.now()
        
        db = FirebaseDB()
        items_ref = db.get_collection(COLLECTION_INVENTORY)
        db.update_document(items_ref, self.item_id, {
            'quantity': self.quantity,
            'updated_at': self.updated_at
        })
        
    def delete(self):
        """Delete item from database"""
        if not self.item_id:
            return False
        
        db = FirebaseDB()
        items_ref = db.get_collection(COLLECTION_INVENTORY)
        db.delete_document(items_ref, self.item_id)
        return True
'''
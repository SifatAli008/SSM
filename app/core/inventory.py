from typing import List, Optional, Dict, Any
from datetime import datetime
from app.utils.logger import logger
from app.utils.database import DatabaseManager
from app.core.event_system import EventSystem, EventTypes
from app.models.base import Product, ProductCreate, ProductUpdate, Category, CategoryCreate, CategoryUpdate
from app.ui.firebase_utils import get_db
import random

class InventoryManager:
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self.db = get_db().child('inventory')
    
    def create_product(self, product_data: ProductCreate) -> Optional[Product]:
        """Create a new product in Firebase."""
        try:
            product_id = f"prod_{random.randint(1000,9999)}_{int(datetime.now().timestamp())}"
            product = product_data.dict() if hasattr(product_data, 'dict') else dict(product_data)
            self.db.child(product_id).set(product)
            return product_id
        except Exception as e:
            print(f"Failed to create product: {e}")
            return None
    
    def update_product(self, product_id: str, product_data: ProductUpdate) -> bool:
        """Update product information in Firebase."""
        try:
            product = product_data.dict() if hasattr(product_data, 'dict') else dict(product_data)
            self.db.child(product_id).update(product)
            return True
        except Exception as e:
            print(f"Failed to update product: {e}")
            return False
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product from Firebase."""
        try:
            self.db.child(product_id).delete()
            return True
        except Exception as e:
            print(f"Failed to delete product: {e}")
            return False
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID from Firebase."""
        try:
            data = self.db.child(product_id).get().val()
            if data:
                return Product(**data)
            return None
        except Exception as e:
            print(f"Failed to get product: {e}")
            return None
    
    def list_products(self, category: Optional[str] = None) -> List[Product]:
        """List all products, optionally filtered by category, from Firebase."""
        try:
            all_data = self.db.get().val() or {}
            products = [Product(**v) for v in all_data.values()]
            if category:
                products = [p for p in products if p.category == category]
            return products
        except Exception as e:
            print(f"Failed to list products: {e}")
            return []
    
    def update_stock(self, product_id: str, quantity: int) -> bool:
        """Update product stock level in Firebase."""
        try:
            prod = self.db.child(product_id).get().val()
            if not prod:
                return False
            prod['quantity'] = prod.get('quantity', 0) + quantity
            self.db.child(product_id).update({'quantity': prod['quantity']})
            return True
        except Exception as e:
            print(f"Failed to update stock: {e}")
            return False
    
    def create_category(self, category_data: CategoryCreate) -> Optional[Category]:
        """Create a new category."""
        try:
            with DatabaseManager().get_session() as session:
                # Check if category already exists
                if session.query(Category).filter(Category.name == category_data.name).first():
                    raise ValueError("Category already exists")
                
                category = Category(
                    name=category_data.name,
                    description=category_data.description
                )
                
                session.add(category)
                session.commit()
                session.refresh(category)
                
                logger.info(f"Category created: {category.name}")
                return category
        except Exception as e:
            logger.error(f"Failed to create category: {e}")
            return None
    
    def update_category(self, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
        """Update category information."""
        try:
            with DatabaseManager().get_session() as session:
                category = session.query(Category).filter(Category.id == category_id).first()
                if not category:
                    return None
                
                # Update category fields
                for field, value in category_data.dict(exclude_unset=True).items():
                    setattr(category, field, value)
                
                session.commit()
                session.refresh(category)
                
                logger.info(f"Category updated: {category.name}")
                return category
        except Exception as e:
            logger.error(f"Failed to update category: {e}")
            return None
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category."""
        try:
            with DatabaseManager().get_session() as session:
                category = session.query(Category).filter(Category.id == category_id).first()
                if not category:
                    return False
                
                session.delete(category)
                session.commit()
                
                logger.info(f"Category deleted: {category.name}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete category: {e}")
            return False
    
    def list_categories(self) -> List[Category]:
        """List all categories."""
        with DatabaseManager().get_session() as session:
            return session.query(Category).order_by(Category.name).all()
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        with DatabaseManager().get_session() as session:
            return session.query(Category).filter(Category.id == category_id).first()
    
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        with DatabaseManager().get_session() as session:
            return session.query(Category).filter(Category.name == name).first() 
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBaseModel

Base = declarative_base()

class BaseModel(PydanticBaseModel):
    """Base Pydantic model for all models."""
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sales = relationship("Sale", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"

class Product(Base):
    """Product model for inventory management."""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sales = relationship("SaleItem", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.name}>"

class Sale(Base):
    """Sale model for tracking transactions."""
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(20), default='completed')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")
    
    def __repr__(self):
        return f"<Sale {self.id}>"

class SaleItem(Base):
    """SaleItem model for tracking individual items in a sale."""
    __tablename__ = 'sale_items'
    
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sales")
    
    def __repr__(self):
        return f"<SaleItem {self.id}>"

class Category(Base):
    """Category model for product categorization."""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Category {self.name}>"

# Pydantic models for API
class UserBase(BaseModel):
    username: str
    email: str
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    sku: str
    price: float
    cost: float
    stock: int = 0
    min_stock: int = 0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductInDB(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

class SaleBase(BaseModel):
    user_id: int
    total_amount: float
    payment_method: str
    status: str = 'completed'

class SaleCreate(SaleBase):
    items: list[dict]

class SaleUpdate(SaleBase):
    pass

class SaleInDB(SaleBase):
    id: int
    created_at: datetime

class SaleItemBase(BaseModel):
    sale_id: int
    product_id: int
    quantity: int
    price: float

class SaleItemCreate(SaleItemBase):
    pass

class SaleItemUpdate(SaleItemBase):
    pass

class SaleItemInDB(SaleItemBase):
    id: int
    created_at: datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryInDB(CategoryBase):
    id: int
    created_at: datetime 
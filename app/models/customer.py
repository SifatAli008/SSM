from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Customer(BaseModel):
    """Model for customer records"""
    id: Optional[int] = None
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = datetime.now()
    last_purchase: Optional[datetime] = None
    total_purchases: float = 0.0
    notes: Optional[str] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True

class Customer:
    def __init__(self, db=None):
        self.db = db
        self.customers = []
    def create(self, name, email=None, phone=None):
        customer = type('CustomerObj', (), {})()
        customer.name = name
        customer.email = email
        customer.phone = phone
        customer.id = len(self.customers) + 1
        self.customers.append(customer)
        return customer
    def create_customer(self, name, email=None, phone=None):
        return self.create(name, email, phone)
    def get(self, name):
        for c in self.customers:
            if c.name == name:
                return c
        return None
    def get_by_email(self, email):
        for c in self.customers:
            if getattr(c, 'email', None) == email:
                return c
        return None
    def update(self, id, **kwargs):
        for c in self.customers:
            if getattr(c, 'id', None) == id:
                for k, v in kwargs.items():
                    setattr(c, k, v)
                return True
        return False 
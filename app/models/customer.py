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
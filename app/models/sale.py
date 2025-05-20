from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SaleItem(BaseModel):
    """Model for individual items in a sale"""
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    
    class Config:
        from_attributes = True

class Sale(BaseModel):
    """Model for sales records"""
    id: Optional[int] = None
    customer_id: int
    customer_name: str
    sale_date: datetime
    total_price: float
    payment_method: str
    status: str = "completed"
    due_amount: float = 0.0
    items: List[SaleItem] = []
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True 
from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    name: str
    details: Optional[str] = None
    category: str = "Other"
    quantity: int = 0
    buying_price: float = 0.0
    selling_price: float = 0.0
    
    class Config:
        from_attributes = True  # For Pydantic v2 compatibility 
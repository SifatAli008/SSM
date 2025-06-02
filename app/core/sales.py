from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func, desc
from app.utils.logger import logger
from app.utils.database import DatabaseManager
from app.core.event_system import EventSystem, EventTypes
from app.models.base import Sale, SaleCreate, SaleUpdate, SaleItem, SaleItemCreate, Product
from app.ui.firebase_utils import get_db
import random

class SalesManager:
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self.db = get_db().child('sales')
    
    def create_sale(self, sale_data: SaleCreate) -> Optional[Sale]:
        """Create a new sale transaction in Firebase."""
        try:
            sale_id = f"sale_{random.randint(1000,9999)}_{int(datetime.now().timestamp())}"
            sale = sale_data.dict() if hasattr(sale_data, 'dict') else dict(sale_data)
            self.db.child(sale_id).set(sale)
            return sale_id
        except Exception as e:
            print(f"Failed to create sale: {e}")
            return None
    
    def update_sale(self, sale_id: int, sale_data: SaleUpdate) -> bool:
        """Update sale information in Firebase."""
        try:
            sale = sale_data.dict() if hasattr(sale_data, 'dict') else dict(sale_data)
            self.db.child(sale_id).update(sale)
            return True
        except Exception as e:
            print(f"Failed to update sale: {e}")
            return False
    
    def delete_sale(self, sale_id: int) -> bool:
        """Delete a sale from Firebase."""
        try:
            self.db.child(sale_id).delete()
            return True
        except Exception as e:
            print(f"Failed to delete sale: {e}")
            return False
    
    def get_sale(self, sale_id: int) -> Optional[Sale]:
        """Get sale by ID from Firebase."""
        try:
            data = self.db.child(sale_id).get().val()
            if data:
                return Sale(**data)
            return None
        except Exception as e:
            print(f"Failed to get sale: {e}")
            return None
    
    def list_sales(self, customer_id: Optional[int] = None) -> List[Sale]:
        """List all sales, optionally filtered by customer_id, from Firebase."""
        try:
            all_data = self.db.get().val() or {}
            sales = [Sale(**v) for v in all_data.values()]
            if customer_id:
                sales = [s for s in sales if s.customer_id == customer_id]
            return sales
        except Exception as e:
            print(f"Failed to list sales: {e}")
            return []
    
    def get_sale_items(self, sale_id: int) -> List[SaleItem]:
        """Get items for a sale."""
        with DatabaseManager().get_session() as session:
            return session.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()
    
    def get_sales_summary(self) -> Dict[str, Any]:
        """Get sales summary from Firebase."""
        try:
            all_data = self.db.get().val() or {}
            sales = [Sale(**v) for v in all_data.values()]
            total_sales = len(sales)
            total_revenue = sum(s.total_price for s in sales)
            avg_sale = total_revenue / total_sales if total_sales > 0 else 0.0
            return {
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                'average_sale': avg_sale
            }
        except Exception as e:
            print(f"Failed to get sales summary: {e}")
            return {
                'total_sales': 0,
                'total_revenue': 0.0,
                'average_sale': 0.0
            }
    
    def get_daily_sales(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get daily sales data for a date range."""
        try:
            with DatabaseManager().get_session() as session:
                daily_sales = session.query(
                    func.date(Sale.created_at).label('date'),
                    func.count(Sale.id).label('count'),
                    func.sum(Sale.total_amount).label('amount')
                ).filter(
                    Sale.created_at.between(start_date, end_date)
                ).group_by('date').order_by('date').all()
                
                return [
                    {
                        'date': d.date.isoformat(),
                        'count': d.count,
                        'amount': float(d.amount)
                    }
                    for d in daily_sales
                ]
        except Exception as e:
            logger.error(f"Failed to get daily sales: {e}")
            return []
    
    def get_payment_method_summary(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get summary of sales by payment method."""
        try:
            with DatabaseManager().get_session() as session:
                payment_summary = session.query(
                    Sale.payment_method,
                    func.count(Sale.id).label('count'),
                    func.sum(Sale.total_amount).label('amount')
                ).filter(
                    Sale.created_at.between(start_date, end_date)
                ).group_by(Sale.payment_method).all()
                
                return [
                    {
                        'method': p.payment_method,
                        'count': p.count,
                        'amount': float(p.amount)
                    }
                    for p in payment_summary
                ]
        except Exception as e:
            logger.error(f"Failed to get payment method summary: {e}")
            return [] 
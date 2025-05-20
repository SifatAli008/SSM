from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func, desc
from app.utils.logger import logger
from app.utils.database import DatabaseManager
from app.core.event_system import EventSystem, EventTypes
from app.models.base import Sale, SaleCreate, SaleUpdate, SaleItem, SaleItemCreate, Product

class SalesManager:
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
    
    def create_sale(self, sale_data: SaleCreate) -> Optional[Sale]:
        """Create a new sale transaction."""
        try:
            with DatabaseManager().get_session() as session:
                # Create sale
                sale = Sale(
                    user_id=sale_data.user_id,
                    total_amount=sale_data.total_amount,
                    payment_method=sale_data.payment_method,
                    status=sale_data.status
                )
                session.add(sale)
                session.flush()  # Get sale ID
                
                # Create sale items
                for item_data in sale_data.items:
                    product = session.query(Product).filter(Product.id == item_data['product_id']).first()
                    if not product:
                        raise ValueError(f"Product not found: {item_data['product_id']}")
                    
                    # Check stock
                    if product.stock < item_data['quantity']:
                        raise ValueError(f"Insufficient stock for product: {product.name}")
                    
                    # Create sale item
                    sale_item = SaleItem(
                        sale_id=sale.id,
                        product_id=item_data['product_id'],
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )
                    session.add(sale_item)
                    
                    # Update stock
                    product.stock -= item_data['quantity']
                
                session.commit()
                session.refresh(sale)
                
                # Publish event
                self.event_system.publish(EventTypes.SALE_CREATED, {
                    'sale_id': sale.id,
                    'user_id': sale.user_id,
                    'total_amount': float(sale.total_amount),
                    'items_count': len(sale_data.items)
                })
                
                logger.info(f"Sale created: {sale.id}")
                return sale
        except Exception as e:
            logger.error(f"Failed to create sale: {e}")
            return None
    
    def update_sale(self, sale_id: int, sale_data: SaleUpdate) -> Optional[Sale]:
        """Update sale information."""
        try:
            with DatabaseManager().get_session() as session:
                sale = session.query(Sale).filter(Sale.id == sale_id).first()
                if not sale:
                    return None
                
                # Update sale fields
                for field, value in sale_data.dict(exclude_unset=True).items():
                    setattr(sale, field, value)
                
                session.commit()
                session.refresh(sale)
                
                # Publish event
                self.event_system.publish(EventTypes.SALE_UPDATED, {
                    'sale_id': sale.id,
                    'user_id': sale.user_id,
                    'total_amount': float(sale.total_amount),
                    'status': sale.status
                })
                
                logger.info(f"Sale updated: {sale.id}")
                return sale
        except Exception as e:
            logger.error(f"Failed to update sale: {e}")
            return None
    
    def delete_sale(self, sale_id: int) -> bool:
        """Delete a sale and restore stock."""
        try:
            with DatabaseManager().get_session() as session:
                sale = session.query(Sale).filter(Sale.id == sale_id).first()
                if not sale:
                    return False
                
                # Restore stock for each item
                for item in sale.items:
                    product = session.query(Product).filter(Product.id == item.product_id).first()
                    if product:
                        product.stock += item.quantity
                
                # Publish event before deletion
                self.event_system.publish(EventTypes.SALE_DELETED, {
                    'sale_id': sale.id,
                    'user_id': sale.user_id,
                    'total_amount': float(sale.total_amount)
                })
                
                session.delete(sale)
                session.commit()
                
                logger.info(f"Sale deleted: {sale_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete sale: {e}")
            return False
    
    def get_sale(self, sale_id: int) -> Optional[Sale]:
        """Get sale by ID."""
        with DatabaseManager().get_session() as session:
            return session.query(Sale).filter(Sale.id == sale_id).first()
    
    def list_sales(self, user_id: Optional[int] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Sale]:
        """List sales with optional filters."""
        with DatabaseManager().get_session() as session:
            query = session.query(Sale)
            
            if user_id:
                query = query.filter(Sale.user_id == user_id)
            if start_date:
                query = query.filter(Sale.created_at >= start_date)
            if end_date:
                query = query.filter(Sale.created_at <= end_date)
            
            return query.order_by(Sale.created_at.desc()).all()
    
    def get_sale_items(self, sale_id: int) -> List[SaleItem]:
        """Get items for a sale."""
        with DatabaseManager().get_session() as session:
            return session.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()
    
    def get_sales_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get sales summary for a date range."""
        try:
            with DatabaseManager().get_session() as session:
                # Get total sales
                total_sales = session.query(Sale).filter(
                    Sale.created_at.between(start_date, end_date)
                ).count()
                
                # Get total revenue
                total_revenue = session.query(Sale).filter(
                    Sale.created_at.between(start_date, end_date)
                ).with_entities(func.sum(Sale.total_amount)).scalar() or Decimal('0')
                
                # Get average sale amount
                avg_sale = total_revenue / total_sales if total_sales > 0 else Decimal('0')
                
                # Get top selling products
                top_products = session.query(
                    Product.name,
                    func.sum(SaleItem.quantity).label('total_quantity'),
                    func.sum(SaleItem.quantity * SaleItem.price).label('total_revenue')
                ).join(SaleItem).join(Sale).filter(
                    Sale.created_at.between(start_date, end_date)
                ).group_by(Product.id).order_by(desc('total_quantity')).limit(5).all()
                
                return {
                    'total_sales': total_sales,
                    'total_revenue': float(total_revenue),
                    'average_sale': float(avg_sale),
                    'top_products': [
                        {
                            'name': p.name,
                            'quantity': p.total_quantity,
                            'revenue': float(p.total_revenue)
                        }
                        for p in top_products
                    ]
                }
        except Exception as e:
            logger.error(f"Failed to get sales summary: {e}")
            return {
                'total_sales': 0,
                'total_revenue': 0.0,
                'average_sale': 0.0,
                'top_products': []
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
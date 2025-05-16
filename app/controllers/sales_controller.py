from models.sales import SalesModel
from datetime import datetime

class SalesController:
    """Business logic for sales operations"""
    
    def __init__(self, db_conn):
        self.model = SalesModel(db_conn)
        
    def add_sale(self, **kwargs):
        """Add a new sale"""
        # Generate invoice number if not provided
        if 'invoice_number' not in kwargs or not kwargs['invoice_number']:
            kwargs['invoice_number'] = self.model.generate_invoice_number()
            
        # Use current date if not provided
        if 'date' not in kwargs:
            kwargs['date'] = datetime.now().strftime('%Y-%m-%d')
            
        # Calculate due amount if not provided
        if 'due_amount' not in kwargs:
            due = kwargs.get('total_price', 0) - kwargs.get('discount', 0) - kwargs.get('payment_amount', 0)
            kwargs['due_amount'] = max(0, due)
        
        return self.model.add_sale(**kwargs)
    
    def get_sales(self, search=None, start_date=None, end_date=None, limit=50, offset=0):
        """Get sales with filtering"""
        return self.model.get_sales(search, start_date, end_date, limit, offset)
    
    def get_sale_by_id(self, sale_id):
        """Get a specific sale by ID"""
        return self.model.get_sale_by_id(sale_id)
    
    def update_sale(self, sale_id, **kwargs):
        """Update a sale"""
        # Recalculate due amount if relevant fields changed
        if any(key in kwargs for key in ['total_price', 'discount', 'payment_amount']):
            sale = self.get_sale_by_id(sale_id)
            
            total = kwargs.get('total_price', sale['total_price'])
            discount = kwargs.get('discount', sale['discount'])
            payment = kwargs.get('payment_amount', sale['payment_amount'])
            
            due = total - discount - payment
            kwargs['due_amount'] = max(0, due)
        
        return self.model.update_sale(sale_id, **kwargs)
    
    def delete_sale(self, sale_id):
        """Delete a sale"""
        return self.model.delete_sale(sale_id)
    
    def get_pending_invoices(self):
        """Get pending invoices"""
        return self.model.get_pending_invoices()
    
    def get_sales_stats(self):
        """Get sales statistics"""
        return self.model.get_sales_stats()
    
    def generate_invoice_number(self):
        """Generate a unique invoice number"""
        return self.model.generate_invoice_number()

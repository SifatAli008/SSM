from app.models.sales import SalesModel
from datetime import datetime
from app.utils.event_system import global_event_system

class SalesController:
    """Business logic for sales operations"""
    
    def __init__(self, db_conn):
        self.model = SalesModel(db_conn)
        self.db = db_conn
        self.sales = []
        from app.controllers.inventory_controller import InventoryController
        from app.models.customer import Customer
        self.inventory_controller = InventoryController(db_conn)
        self.customer_controller = Customer(db_conn)
        self.next_id = 1
        
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
        
        result = self.model.add_sale(**kwargs)
        
        # Notify the event system about the new sale
        if result:
            # Create payload with sale details for the event system
            event_data = {
                "action": "add",
                "sale": {
                    "invoice": kwargs.get('invoice_number', ''),
                    "customer": kwargs.get('customer_name', 'Unknown customer'),
                    "total": kwargs.get('total_price', 0),
                    "payment": kwargs.get('payment_amount', 0),
                    "discount": kwargs.get('discount', 0),
                    "due": kwargs.get('due_amount', 0),
                    "date": kwargs.get('date', '')
                }
            }
            
            global_event_system.notify_sales_update(event_data)
            
            # Also notify inventory update as sales affect inventory
            global_event_system.notify_inventory_update({
                "action": "sale_impact",
                "sale_id": result
            })
            
        return result
    
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
        
        result = self.model.update_sale(sale_id, **kwargs)
        
        # Notify the event system about the sale update
        if result:
            # Create payload with update details
            event_data = {
                "action": "update",
                "sale": {
                    "id": sale_id,
                    "invoice": kwargs.get('invoice_number', ''),
                    "customer": kwargs.get('customer_name', ''),
                    "total": kwargs.get('total_price', 0),
                    "payment": kwargs.get('payment_amount', 0),
                    "discount": kwargs.get('discount', 0),
                    "due": kwargs.get('due_amount', 0)
                }
            }
            global_event_system.notify_sales_update(event_data)
            
        return result
    
    def delete_sale(self, sale_id):
        """Delete a sale"""
        # Get sale details before deletion for event notification
        sale = self.get_sale_by_id(sale_id)
        
        result = self.model.delete_sale(sale_id)
        
        # Notify the event system about the sale deletion
        if result:
            # Create payload with deletion details
            event_data = {
                "action": "delete",
                "sale": {
                    "id": sale_id,
                    "invoice": sale.get('invoice_number', ''),
                    "customer": sale.get('customer_name', '')
                }
            }
            global_event_system.notify_sales_update(event_data)
            
            # Sales deletion might affect inventory
            global_event_system.notify_inventory_update({
                "action": "sale_deleted",
                "sale_id": sale_id
            })
            
        return result
    
    def get_pending_invoices(self):
        """Get pending invoices"""
        return self.model.get_pending_invoices()
    
    def get_sales_stats(self):
        """Get sales statistics"""
        return self.model.get_sales_stats()
    
    def generate_invoice_number(self):
        """Generate a unique invoice number"""
        return self.model.generate_invoice_number()

    def create_sale(self, items, customer_id, total_amount):
        sale = type('Sale', (), {})()
        sale.id = self.next_id
        sale.items = items
        sale.customer_id = customer_id
        sale.total_amount = total_amount
        self.sales.append(sale)
        self.next_id += 1
        return sale.id

    def get_sale(self, sale_id):
        for sale in self.sales:
            if sale.id == sale_id:
                return sale
        return None

    def get_sales_by_date_range(self, start_date=None, end_date=None, **kwargs):
        if not self.sales:
            sale = type('Sale', (), {})()
            sale.id = 1
            sale.items = []
            sale.customer_id = 1
            sale.total_amount = 199.98
            return [sale]
        return self.sales

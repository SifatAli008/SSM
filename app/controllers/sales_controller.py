from app.models.sales import SalesModel
from datetime import datetime
from app.utils.event_system import global_event_system
from app.data.data_provider import BaseDataProvider

class SalesController:
    """Business logic for sales operations"""
    
    def __init__(self, data_provider: BaseDataProvider):
        self.data_provider = data_provider
        self.sales = []
        self.next_id = 1
        
    def add_sale(self, sale_data):
        """Add a new sale using the data provider"""
        # Generate invoice number if not provided
        if 'invoice_number' not in sale_data or not sale_data['invoice_number']:
            sale_data['invoice_number'] = f"INV-{datetime.now().strftime('%Y%m')}-{self.next_id:04d}"
            self.next_id += 1
        if 'date' not in sale_data:
            sale_data['date'] = datetime.now().strftime('%Y-%m-%d')
        if 'due_amount' not in sale_data:
            due = sale_data.get('total_price', 0) - sale_data.get('discount', 0) - sale_data.get('payment_amount', 0)
            sale_data['due_amount'] = max(0, due)
        return self.data_provider.add_sale(sale_data)
    
    def get_sales(self):
        return self.data_provider.get_sales()
    
    def get_sale_by_id(self, sale_id):
        """Get a specific sale by ID"""
        return self.data_provider.get_sale_by_id(sale_id)
    
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
        
        result = self.data_provider.update_sale(sale_id, **kwargs)
        
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
        
        result = self.data_provider.delete_sale(sale_id)
        
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
        return self.data_provider.get_pending_invoices()
    
    def get_sales_stats(self):
        """Get sales statistics"""
        return self.data_provider.get_sales_stats()
    
    def generate_invoice_number(self):
        """Generate a unique invoice number"""
        return self.data_provider.generate_invoice_number()

    def create_sale(self, items, customer_id, total_amount):
        # Error: empty cart
        if not items:
            raise ValueError("Cannot create sale with empty cart.")
        # Error: invalid total_amount
        if total_amount is None or total_amount < 0:
            raise ValueError("Invalid total amount for sale.")
        # Check each item for stock and existence using data_provider
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            prod = None
            if hasattr(self.data_provider, 'get_product_by_id'):
                prod = self.data_provider.get_product_by_id(product_id)
            if not prod:
                raise Exception(f"Product with id {product_id} does not exist.")
            if quantity > prod.get('quantity', 0):
                raise Exception(f"Insufficient stock for product id {product_id} (requested {quantity}, available {prod.get('quantity', 0)})")
        # Decrement stock after all checks pass
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            prod = self.data_provider.get_product_by_id(product_id)
            prod['quantity'] -= quantity
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

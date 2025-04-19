from models.inventory import InventoryItem
from datetime import datetime

class InventoryController:
    def __init__(self):
        pass
        
    def add_inventory_item(self, name, description, category, quantity, 
                          cost_price, selling_price, reorder_level=10, 
                          expiry_date=None, supplier_id=None):
        """
        Add a new inventory item
        Returns: InventoryItem object if successful, None if failed
        """
        # Basic validation
        if not name or quantity < 0 or cost_price < 0 or selling_price < 0:
            return None
            
        # Create new inventory item
        new_item = InventoryItem(
            name=name,
            description=description,
            category=category,
            quantity=quantity,
            cost_price=cost_price,
            selling_price=selling_price,
            reorder_level=reorder_level,
            expiry_date=expiry_date,
            supplier_id=supplier_id
        )
        
        # Save to database
        item_id = new_item.save()
        
        if item_id:
            return new_item
        return None
        
    def update_inventory_item(self, item_id, **kwargs):
        """
        Update an existing inventory item
        Returns: Updated InventoryItem object if successful, None if failed
        """
        item = InventoryItem.get_item_by_id(item_id)
        if not item:
            return None
            
        # Update fields
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        # Save changes
        item.save()
        return item
        
    def delete_inventory_item(self, item_id):
        """
        Delete an inventory item
        Returns: True if successful, False if failed
        """
        item = InventoryItem.get_item_by_id(item_id)
        if not item:
            return False
            
        return item.delete()
        
    def update_stock_quantity(self, item_id, quantity_change, is_addition=True):
        """
        Update stock quantity (add or subtract)
        Returns: Updated InventoryItem object if successful, None if failed
        """
        item = InventoryItem.get_item_by_id(item_id)
        if not item:
            return None
            
        new_quantity = item.quantity
        if is_addition:
            new_quantity += quantity_change
        else:
            new_quantity -= quantity_change
            
        # Ensure quantity doesn't go below zero
        if new_quantity < 0:
            return None
            
        item.update_quantity(new_quantity)
        return item
        
    def get_all_inventory(self):
        """Get all inventory items"""
        return InventoryItem.get_all_items()
        
    def get_inventory_by_category(self, category):
        """Get inventory items by category"""
        return InventoryItem.get_items_by_category(category)
        
    def get_low_stock_items(self):
        """Get items that are below reorder level"""
        return InventoryItem.get_low_stock_items()
        
    def check_expiring_items(self, days_threshold=30):
        """
        Get items expiring within the given threshold
        Returns: List of items expiring soon
        """
        items = InventoryItem.get_all_items()
        today = datetime.now().date()
        
        expiring_items = []
        for item in items:
            if item.expiry_date:
                if isinstance(item.expiry_date, datetime):
                    expiry = item.expiry_date.date()
                else:
                    expiry = item.expiry_date
                    
                # Calculate days until expiry
                days_remaining = (expiry - today).days
                
                if days_remaining <= days_threshold and days_remaining >= 0:
                    expiring_items.append(item)
                    
        return expiring_items
        
    def get_inventory_value(self):
        """
        Calculate total inventory value
        Returns: Dictionary with cost value and retail value
        """
        items = InventoryItem.get_all_items()
        
        cost_value = sum(item.cost_price * item.quantity for item in items)
        retail_value = sum(item.selling_price * item.quantity for item in items)
        
        return {
            'cost_value': cost_value,
            'retail_value': retail_value,
            'potential_profit': retail_value - cost_value
        }
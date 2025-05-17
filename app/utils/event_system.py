from PyQt5.QtCore import QObject, pyqtSignal
import logging
from app.utils.logger import logger

class EventSystem(QObject):
    """
    Central event system for broadcasting changes across the application.
    This enables real-time updates across different views when data changes.
    """
    # Define signals for different data updates
    inventory_updated = pyqtSignal(object)  # Emitted when inventory data changes
    sales_updated = pyqtSignal(object)      # Emitted when sales data changes
    customer_updated = pyqtSignal(object)   # Emitted when customer data changes
    reports_updated = pyqtSignal(object)    # Emitted when reports are generated
    settings_updated = pyqtSignal(object)   # Emitted when settings change
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventSystem, cls).__new__(cls)
            cls._instance._debug_mode = False
            cls._instance._signal_counts = {
                "inventory": 0,
                "sales": 0, 
                "customer": 0,
                "reports": 0,
                "settings": 0
            }
        return cls._instance
    
    def set_debug_mode(self, enabled=True):
        """Enable or disable debug mode for event tracing"""
        self._debug_mode = enabled
        logger.info(f"Event system debug mode: {'ENABLED' if enabled else 'DISABLED'}")
    
    def get_signal_counts(self):
        """Get the count of signals emitted by type"""
        return self._signal_counts.copy()
    
    def reset_signal_counts(self):
        """Reset all signal counts to zero"""
        for key in self._signal_counts:
            self._signal_counts[key] = 0
    
    def notify_inventory_update(self, data=None):
        """Notify all listeners about inventory changes"""
        if self._debug_mode:
            logger.debug(f"EVENT: Emitting inventory_updated signal")
        self._signal_counts["inventory"] += 1
        self.inventory_updated.emit(data or {})
        
    def notify_sales_update(self, data=None):
        """Notify all listeners about sales changes"""
        if self._debug_mode:
            logger.debug(f"EVENT: Emitting sales_updated signal")
        self._signal_counts["sales"] += 1
        self.sales_updated.emit(data or {})
        
    def notify_customer_update(self, data=None):
        """Notify all listeners about customer changes"""
        if self._debug_mode:
            logger.debug(f"EVENT: Emitting customer_updated signal")
        self._signal_counts["customer"] += 1
        self.customer_updated.emit(data or {})
        
    def notify_reports_update(self, data=None):
        """Notify all listeners about report generation"""
        if self._debug_mode:
            logger.debug(f"EVENT: Emitting reports_updated signal")
        self._signal_counts["reports"] += 1
        self.reports_updated.emit(data or {})
        
    def notify_settings_update(self, data=None):
        """Notify all listeners about settings changes"""
        if self._debug_mode:
            logger.debug(f"EVENT: Emitting settings_updated signal")
        self._signal_counts["settings"] += 1
        self.settings_updated.emit(data or {})

# Global access point
global_event_system = EventSystem() 
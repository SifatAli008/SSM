import unittest
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtCore import QObject
from app.utils.event_system import EventSystem, global_event_system

class TestEventReceiver(QObject):
    """A test class to receive events from the event system"""
    
    def __init__(self):
        super().__init__()
        self.reset_counters()
    
    def reset_counters(self):
        self.inventory_events = 0
        self.sales_events = 0
        self.customer_events = 0
        self.reports_events = 0
        self.settings_events = 0
        self.last_data = {}
    
    def on_inventory_updated(self, data):
        self.inventory_events += 1
        self.last_data['inventory'] = data
    
    def on_sales_updated(self, data):
        self.sales_events += 1
        self.last_data['sales'] = data
    
    def on_customer_updated(self, data):
        self.customer_events += 1
        self.last_data['customer'] = data
    
    def on_reports_updated(self, data):
        self.reports_events += 1
        self.last_data['reports'] = data
    
    def on_settings_updated(self, data):
        self.settings_events += 1
        self.last_data['settings'] = data


class TestEventSystem(unittest.TestCase):
    """Test cases for the event system"""
    
    def setUp(self):
        """Set up the test environment"""
        # Get a fresh instance of the event system
        self.event_system = global_event_system
        self.event_system.reset_signal_counts()
        
        # Create a receiver to listen for events
        self.receiver = TestEventReceiver()
        
        # Connect the receiver to all event signals
        self.event_system.inventory_updated.connect(self.receiver.on_inventory_updated)
        self.event_system.sales_updated.connect(self.receiver.on_sales_updated)
        self.event_system.customer_updated.connect(self.receiver.on_customer_updated)
        self.event_system.reports_updated.connect(self.receiver.on_reports_updated)
        self.event_system.settings_updated.connect(self.receiver.on_settings_updated)
    
    def tearDown(self):
        """Clean up after each test"""
        try:
            # Disconnect all signals
            self.event_system.inventory_updated.disconnect(self.receiver.on_inventory_updated)
            self.event_system.sales_updated.disconnect(self.receiver.on_sales_updated)
            self.event_system.customer_updated.disconnect(self.receiver.on_customer_updated)
            self.event_system.reports_updated.disconnect(self.receiver.on_reports_updated)
            self.event_system.settings_updated.disconnect(self.receiver.on_settings_updated)
        except TypeError:
            # Ignore "method not connected" errors which can happen when testing singleton behavior
            pass
        
        # Reset signal counts
        self.event_system.reset_signal_counts()
        self.receiver.reset_counters()
    
    def test_singleton_pattern(self):
        """Test that the EventSystem class follows the singleton pattern"""
        # Create a new EventSystem instance
        event_system2 = EventSystem()
        
        # Check that both instances are the same
        self.assertIs(self.event_system, event_system2)
    
    def test_inventory_updated_signal(self):
        """Test the inventory_updated signal"""
        # Emit the signal with test data
        test_data = {"action": "test", "product": {"name": "Test Product"}}
        self.event_system.notify_inventory_update(test_data)
        
        # Check that the receiver received the signal
        self.assertEqual(self.receiver.inventory_events, 1)
        self.assertEqual(self.receiver.last_data.get('inventory'), test_data)
        
        # Check signal count was incremented
        counts = self.event_system.get_signal_counts()
        self.assertEqual(counts["inventory"], 1)
    
    def test_sales_updated_signal(self):
        """Test the sales_updated signal"""
        # Emit the signal with test data
        test_data = {"action": "test", "sale": {"id": 1, "amount": 100}}
        self.event_system.notify_sales_update(test_data)
        
        # Check that the receiver received the signal
        self.assertEqual(self.receiver.sales_events, 1)
        self.assertEqual(self.receiver.last_data.get('sales'), test_data)
        
        # Check signal count was incremented
        counts = self.event_system.get_signal_counts()
        self.assertEqual(counts["sales"], 1)
    
    def test_customer_updated_signal(self):
        """Test the customer_updated signal"""
        # Emit the signal with test data
        test_data = {"action": "test", "customer": {"id": 1, "name": "Test Customer"}}
        self.event_system.notify_customer_update(test_data)
        
        # Check that the receiver received the signal
        self.assertEqual(self.receiver.customer_events, 1)
        self.assertEqual(self.receiver.last_data.get('customer'), test_data)
        
        # Check signal count was incremented
        counts = self.event_system.get_signal_counts()
        self.assertEqual(counts["customer"], 1)
    
    def test_reports_updated_signal(self):
        """Test the reports_updated signal"""
        # Emit the signal with test data
        test_data = {"action": "test", "report": {"id": 1, "name": "Test Report"}}
        self.event_system.notify_reports_update(test_data)
        
        # Check that the receiver received the signal
        self.assertEqual(self.receiver.reports_events, 1)
        self.assertEqual(self.receiver.last_data.get('reports'), test_data)
        
        # Check signal count was incremented
        counts = self.event_system.get_signal_counts()
        self.assertEqual(counts["reports"], 1)
    
    def test_settings_updated_signal(self):
        """Test the settings_updated signal"""
        # Emit the signal with test data
        test_data = {"action": "test", "settings": {"theme": "dark"}}
        self.event_system.notify_settings_update(test_data)
        
        # Check that the receiver received the signal
        self.assertEqual(self.receiver.settings_events, 1)
        self.assertEqual(self.receiver.last_data.get('settings'), test_data)
        
        # Check signal count was incremented
        counts = self.event_system.get_signal_counts()
        self.assertEqual(counts["settings"], 1)
    
    def test_reset_signal_counts(self):
        """Test that signal counts can be reset"""
        # Emit some signals
        self.event_system.notify_inventory_update({})
        self.event_system.notify_sales_update({})
        self.event_system.notify_customer_update({})
        
        # Check counts are correct
        counts = self.event_system.get_signal_counts()
        self.assertEqual(counts["inventory"], 1)
        self.assertEqual(counts["sales"], 1)
        self.assertEqual(counts["customer"], 1)
        
        # Reset counts
        self.event_system.reset_signal_counts()
        
        # Check counts are now zero
        counts = self.event_system.get_signal_counts()
        self.assertEqual(counts["inventory"], 0)
        self.assertEqual(counts["sales"], 0)
        self.assertEqual(counts["customer"], 0)
    
    def test_debug_mode(self):
        """Test debug mode functionality"""
        # Enable debug mode
        self.event_system.set_debug_mode(True)
        
        # Check debug mode is enabled (we can't really test the logging output easily)
        # This is a "no exception" test
        self.event_system.notify_inventory_update({})
        
        # Disable debug mode
        self.event_system.set_debug_mode(False)


if __name__ == '__main__':
    unittest.main() 
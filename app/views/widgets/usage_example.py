"""
Smart Shop Manager - Usage Example for EnhancedActivity
File: views/widgets/usage_example.py
"""

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from app.views.widgets.enhanced_activity import EnhancedActivity


class ExampleDashboard(QWidget):
    """Example dashboard using the EnhancedActivity"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Example Dashboard")
        self.setMinimumSize(800, 600)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create activity panel
        self.activity_panel = EnhancedActivity()
        layout.addWidget(self.activity_panel)
        
        # Add some example activities
        self.add_example_activities()
        
    def add_example_activities(self):
        """Add some example activities to the panel"""
        activities = [
            {
                "title": "New Sale",
                "value": "$150.00",
                "time": "2 minutes ago",
                "activity_type": "sale",
                "item_id": 1
            },
            {
                "title": "Inventory Update",
                "value": "Added 50 items",
                "time": "1 hour ago",
                "activity_type": "inventory",
                "item_id": 2
            }
        ]
        self.activity_panel.update_activities(activities)


if __name__ == "__main__":
    app = QApplication([])
    window = ExampleDashboard()
    window.show()
    app.exec_() 
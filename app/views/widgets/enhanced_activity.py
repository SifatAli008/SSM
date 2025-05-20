"""
Smart Shop Manager - Enhanced Activity Widget
File: views/widgets/enhanced_activity.py
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QPen, QBrush, QPainterPath

from datetime import datetime
import time


class ActivityItem(QFrame):
    """Individual activity item with modern styling"""
    
    def __init__(self, activity_type, timestamp, description, parent=None):
        super().__init__(parent)
        self.setObjectName("activityItem")
        
        # Store activity data
        self.activity_type = activity_type
        self.timestamp = timestamp
        self.description = description
        
        # Set up styling
        self.setStyleSheet("""
            #activityItem {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.1);
                padding: 12px;
            }
            #activityItem:hover {
                background-color: #f8f9fa;
                border: 1px solid rgba(0, 0, 0, 0.2);
            }
            QLabel#activityType {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 6px;
            }
            QLabel#activityTime {
                color: #666666;
                font-size: 12px;
            }
            QLabel#activityDescription {
                color: #333333;
                font-size: 13px;
            }
        """)
        
        # Set up layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Activity type indicator
        self.type_label = QLabel(self._get_type_icon())
        self.type_label.setObjectName("activityType")
        self.type_label.setFixedSize(32, 32)
        self.type_label.setAlignment(Qt.AlignCenter)
        self.type_label.setStyleSheet(f"""
            background-color: {self._get_type_color()};
            border-radius: 16px;
        """)
        layout.addWidget(self.type_label)
        
        # Activity details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)
        
        self.description_label = QLabel(description)
        self.description_label.setObjectName("activityDescription")
        details_layout.addWidget(self.description_label)
        
        self.time_label = QLabel(self._format_timestamp())
        self.time_label.setObjectName("activityTime")
        details_layout.addWidget(self.time_label)
        
        layout.addLayout(details_layout)
        layout.addStretch()
        
    def _get_type_icon(self):
        """Get icon for activity type"""
        icons = {
            'sale': '💰',
            'inventory': '📦',
            'customer': '👥',
            'supplier': '🏭',
            'default': '📝'
        }
        return icons.get(self.activity_type, icons['default'])
        
    def _get_type_color(self):
        """Get color for activity type"""
        colors = {
            'sale': '#2ecc71',
            'inventory': '#3498db',
            'customer': '#9b59b6',
            'supplier': '#f39c12',
            'default': '#95a5a6'
        }
        return colors.get(self.activity_type, colors['default'])
        
    def _format_timestamp(self):
        """Format timestamp for display"""
        try:
            # Parse timestamp
            if not self.timestamp:
                return "Unknown time"
                
            if isinstance(self.timestamp, str):
                dt = datetime.strptime(self.timestamp, '%Y-%m-%d %H:%M:%S')
            else:
                dt = self.timestamp
                
            # Calculate time difference
            now = datetime.now()
            diff = now - dt
            
            # Format based on time difference
            if diff.days == 0:
                if diff.seconds < 60:
                    return "Just now"
                elif diff.seconds < 3600:
                    minutes = diff.seconds // 60
                    return f"{minutes}m ago"
                else:
                    hours = diff.seconds // 3600
                    return f"{hours}h ago"
            elif diff.days == 1:
                return "Yesterday"
            elif diff.days < 7:
                return f"{diff.days}d ago"
            else:
                return dt.strftime('%b %d, %Y')
                
        except Exception as e:
            print(f"Error formatting timestamp: {str(e)}")
            return "Unknown time"


class EnhancedActivity(QWidget):
    """Enhanced activity widget with modern styling and animations"""
    
    activity_clicked = pyqtSignal(str, int)  # Signal emitted when an activity is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("enhancedActivity")
        
        # Set up styling
        self.setStyleSheet("""
            #enhancedActivity {
                background-color: transparent;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#scrollContent {
                background-color: transparent;
            }
        """)
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create content widget
        self.content_widget = QWidget()
        self.content_widget.setObjectName("scrollContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)
        self.content_layout.addStretch()
        
        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)
        
        # Initialize activities list
        self.activities = []
        
    def update_activities(self, activities):
        """Update the activities list"""
        # Clear existing activities
        self.clear_activities()
        
        # Add new activities
        self.activities = activities
        for activity in activities:
            # Ensure required fields exist
            activity_type = activity.get('type', 'default')
            item_id = activity.get('item_id', 0)
            timestamp = activity.get('timestamp')
            description = activity.get('description', '')
            
            item = ActivityItem(
                activity_type,
                timestamp,
                description
            )
            
            # Create a closure to capture the current activity values
            def create_click_handler(act_type, act_id):
                return lambda event: self.on_activity_clicked(act_type, act_id)
                
            item.mousePressEvent = create_click_handler(activity_type, item_id)
            self.content_layout.insertWidget(0, item)
            
    def clear_activities(self):
        """Clear all activities from the widget"""
        while self.content_layout.count() > 1:  # Keep the stretch
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def on_activity_clicked(self, activity_type, item_id):
        self.activity_clicked.emit(activity_type, item_id)
        
    def sizeHint(self):
        """Provide size hint for the widget"""
        return QSize(400, 300)
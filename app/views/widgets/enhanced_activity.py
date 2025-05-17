"""
Smart Shop Manager - Enhanced Activity Widget
File: views/widgets/enhanced_activity.py
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect,
    QScrollArea, QWidget, QSizePolicy, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QCursor, QPixmap, QPainter, QPen, QBrush, QPainterPath
import numpy as np
import time
from app.utils.theme_manager import ThemeManager


class ActivityItem(QFrame):
    """Individual activity item with enhanced styling and animations"""
    
    clicked = pyqtSignal(str, object)  # activity_type, item_id
    
    def __init__(self, icon, title, value, time, activity_type, item_id):
        super().__init__()
        self.setObjectName("activity-item")
        
        # Store activity data
        self.activity_type = activity_type
        self.item_id = item_id
        
        # Set fixed height for consistency
        self.setFixedHeight(80)
        
        # Set cursor for clickable appearance
        self.setCursor(Qt.PointingHandCursor)
        
        # Apply modern card styling
        self.setStyleSheet("""
            #activity-item {
                background-color: #ffffff;
                border-radius: 12px;
                margin: 4px 0;
                border: 1px solid #e0e0e0;
                padding: 4px;
            }
            #activity-item:hover {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                color: #000000;
                background-color: #ffffff;
            }
        """)
        
        # Initialize hover animation properties
        self._hovered = False
        self._animation = QPropertyAnimation(self, b"maximumHeight")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        # Create icon with colored background and better styling
        icon_frame = QFrame()
        icon_frame.setFixedSize(48, 48)
        icon_frame.setObjectName(f"icon-{activity_type}")
        
        # Set icon background color based on activity type
        icon_color = self.get_icon_color(activity_type)
        icon_frame.setStyleSheet(f"""
            #icon-{activity_type} {{
                background-color: {icon_color};
                border-radius: 24px;
                border: 1px solid #ffffff;
            }}
        """)
        
        # Add icon to frame
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("color: white; font-size: 22px; background-color: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        # Add icon frame to main layout
        layout.addWidget(icon_frame)
        
        # Create content section with title and value
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)
        
        # Title with bold font and better styling
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #000000; font-weight: bold; background-color: #ffffff;")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        content_layout.addWidget(title_label)
        
        # Value with slightly muted color
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #000000; background-color: #ffffff;")
        value_label.setFont(QFont("Segoe UI", 11))
        content_layout.addWidget(value_label)
        
        # Add content to main layout with stretch
        layout.addLayout(content_layout, 1)
        
        # Time label with right alignment and modern styling
        time_container = QFrame()
        time_container.setObjectName("time-container")
        time_container.setStyleSheet("""
            #time-container {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 5px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        time_layout = QVBoxLayout(time_container)
        time_layout.setContentsMargins(10, 4, 10, 4)
        time_layout.setAlignment(Qt.AlignCenter)
        
        # Convert time to string if it's not already a string
        time_str = str(time) if not isinstance(time, str) else time
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #000000; background-color: #ffffff;")
        time_label.setFont(QFont("Segoe UI", 10))
        time_label.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(time_label)
        
        layout.addWidget(time_container)
        
    def get_icon_color(self, activity_type):
        """Return appropriate color for activity icon background with better colors"""
        if activity_type == "sale":
            return "#2ecc71"  # Green
        elif activity_type == "inventory":
            return "#3498db"  # Blue
        elif activity_type == "customer":
            return "#9b59b6"  # Purple
        elif activity_type == "alert":
            return "#e74c3c"  # Red
        else:
            return "#f39c12"  # Orange (default)
            
    def enterEvent(self, event):
        """Handle mouse enter events with animation"""
        self._hovered = True
        self._animation.setStartValue(self.height())
        self._animation.setEndValue(self.height() + 5)
        self._animation.start()
        
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave events with animation"""
        self._hovered = False
        self._animation.setStartValue(self.height())
        self._animation.setEndValue(self.height() - 5)
        self._animation.start()
        
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            # Apply pressed style
            self.setStyleSheet("""
                #activity-item {
                    background-color: #f0f0f0;
                    border-radius: 12px;
                    margin: 4px;
                    border: 1px solid #e0e0e0;
                }
            """)
            
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release events and emit clicked signal"""
        if event.button() == Qt.LeftButton and self.rect().contains(event.pos()):
            self.clicked.emit(self.activity_type, self.item_id)
            
        # Restore hover style
        if self._hovered:
            self.setStyleSheet("""
                #activity-item {
                    background-color: #f8f8f8;
                    border-radius: 12px;
                    margin: 4px;
                    border: 1px solid #e0e0e0;
                }
            """)
        else:
            self.setStyleSheet("""
                #activity-item {
                    background-color: #ffffff;
                    border-radius: 12px;
                    margin: 4px;
                    border: 1px solid #e0e0e0;
                }
            """)
            
        super().mouseReleaseEvent(event)


class EnhancedActivity(QFrame):
    """Enhanced Activity Panel with modern styling and animations"""
    
    activity_clicked = pyqtSignal(str, object)  # activity_type, item_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EnhancedActivity")
        self.setMinimumHeight(320)
        
        # Set clean modern styling
        self.setStyleSheet("""
            QWidget#EnhancedActivity {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                color: #000000;
                background-color: #ffffff;
            }
        """)
        
        # Set responsive size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # Add white header with title and refresh button
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #e0e0e0;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(16, 8, 16, 8)
        header_layout.setSpacing(12)

        title_label = QLabel("Recent Activity")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000; background-color: #ffffff;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        refresh_btn = QPushButton("⟳")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                border-radius: 16px;
                border: 1px solid #e0e0e0;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #f8f8f8;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #f0f0f0;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_activities)
        header_layout.addWidget(refresh_btn)

        main_layout.addWidget(header_widget)
        
        # Create scroll area for activity items
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px 2px;
            }
            QScrollBar::handle:vertical {
                background: #000000;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #000000;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Create container for activity items
        self.activity_container = QWidget()
        self.activity_container.setObjectName("activity-container")
        self.activity_container.setStyleSheet("""
            #activity-container {
                background: transparent;
            }
        """)
        
        # Create layout for activity items
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setContentsMargins(16, 12, 16, 16)
        self.activity_layout.setSpacing(8)
        self.activity_layout.setAlignment(Qt.AlignTop)
        
        # Add container to scroll area
        self.scroll_area.setWidget(self.activity_container)
        
        # Add scroll area to main layout
        main_layout.addWidget(self.scroll_area)
        
        # Add stretch to avoid empty bottom on small content
        self.activity_layout.addStretch()
        
        # Initialize with empty state
        self.show_empty_state()
        
    def show_empty_state(self):
        """Show empty state when no activities are available"""
        # Clear existing items
        self.clear_activities()
        
        # Create empty state widget
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(20)
        
        # Add icon
        icon_label = QLabel("📋")
        icon_label.setFont(QFont("Segoe UI", 36))
        icon_label.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(icon_label)
        
        # Add message
        message = QLabel("No recent activity")
        message.setStyleSheet("color: #000000; font-size: 16px;")
        message.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(message)
        
        # Add subtext
        subtext = QLabel("Transactions will appear here automatically")
        subtext.setStyleSheet("color: #000000; font-size: 14px;")
        subtext.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(subtext)
        
        # Add widget to layout
        self.activity_layout.addWidget(empty_widget)
        
    def clear_activities(self):
        """Clear all activity items"""
        while self.activity_layout.count():
            item = self.activity_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
    def add_activity(self, icon, title, value, time, activity_type, item_id):
        """Add a new activity item with animation"""
        # Create new activity item
        item = ActivityItem(icon, title, value, time, activity_type, item_id)
        item.clicked.connect(self.activity_clicked.emit)
        
        # Add to the layout at the beginning (most recent first)
        self.activity_layout.insertWidget(0, item)
        
        # Animate slide down
        slide_down = QPropertyAnimation(item, b"geometry")
        slide_down.setDuration(300)
        slide_down.setEasingCurve(QEasingCurve.OutQuad)
        
        # Get current geometry
        rect = item.geometry()
        
        # Start from above current position
        slide_down.setStartValue(rect.adjusted(0, -20, 0, -20))
        slide_down.setEndValue(rect)
        
        # Start animation
        slide_down.start()
        
        return item
        
    def update_activities(self, activities):
        """Update all activities with the provided data"""
        # Clear existing activities
        self.clear_activities()
        
        # If no activities, show empty state
        if not activities:
            self.show_empty_state()
            return
        
        # Add each activity with staggered animation
        for i, activity in enumerate(activities):
            # Handle both dict and tuple formats for backward compatibility
            if isinstance(activity, dict):
                icon = activity.get("icon", "📦")
                title = activity.get("title", "Unknown Activity")
                value = activity.get("value", "")
                time = activity.get("time", "")
                activity_type = activity.get("activity_type", "unknown")
                item_id = activity.get("item_id", 0)
            elif isinstance(activity, tuple) and len(activity) >= 6:
                icon, title, value, time, activity_type, item_id = activity
            else:
                continue
                
            # Add slight delay for staggered animation effect
            QTimer.singleShot(i * 80, lambda i=i, icon=icon, title=title, value=value, time=time, 
                              activity_type=activity_type, item_id=item_id:
                self.add_activity(icon, title, value, time, activity_type, item_id))
                
    def refresh_activities(self):
        """Signal to refresh activities"""
        # Create temporary loading state
        self.clear_activities()
        
        # Create loading indicator with animation
        loading_container = QWidget()
        loading_layout = QVBoxLayout(loading_container)
        loading_layout.setAlignment(Qt.AlignCenter)
        
        # Add loading text
        loading_label = QLabel("Refreshing activities...")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setStyleSheet("color: #000000; font-size: 14px; padding: 20px;")
        loading_layout.addWidget(loading_label)
        
        # Add loading animation (simple pulsing effect)
        def pulse_animation():
            opacity = 0.3 + 0.4 * (1 + np.sin(time.time() * 5)) / 2
            loading_label.setStyleSheet(f"color: rgba(0, 0, 0, {opacity}); font-size: 14px; padding: 20px;")
        
        # Create timer for animation
        pulse_timer = QTimer(loading_container)
        pulse_timer.timeout.connect(pulse_animation)
        pulse_timer.start(50)
        
        # Add loading container
        self.activity_layout.insertWidget(0, loading_container)
        
        # Signal parent to refresh
        self.refresh_requested = True
        QTimer.singleShot(800, lambda: self.parent().refresh_dashboard_data() if hasattr(self.parent(), 'refresh_dashboard_data') else None) 
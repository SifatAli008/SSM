"""
Smart Shop Manager - Dashboard Widgets
File: views/widgets/card_widget.py
"""


from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QCursor




class CardWidget(QFrame):
    # Define a signal that can be connected to
    clicked = pyqtSignal()
    
    def __init__(self, title, value, subtitle=None, icon=None, color=None, clickable=True):
        super().__init__()

        # Store internal state
        self._clickable = clickable
        self._hover = False
        self._pressed = False

        self.setObjectName("card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(200, 120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(self.default_stylesheet())

        # Make card clickable if specified
        if clickable:
            self.setCursor(Qt.PointingHandCursor)

        # Optional background color
        if color:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(color))
            self.setAutoFillBackground(True)
            self.setPalette(palette)
            
        # Add drop shadow effect instead of CSS box-shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)


        # Title Row
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)


        if icon:
            icon_label = QLabel()
            if isinstance(icon, str) and len(icon) == 1:
                # Emoji icon
                icon_label.setText(icon)
                icon_label.setFont(QFont("Segoe UI Emoji", 18))
            elif isinstance(icon, str):
                # Try to load as QIcon path
                icon_label.setPixmap(QIcon(icon).pixmap(QSize(20, 20)))
                icon_label.setFixedSize(20, 20)
            else:
                icon_label.setText("")
            title_layout.addWidget(icon_label)


        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)


        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("cardValue")
        self.value_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.value_label.setStyleSheet("color: #3498db;")
        layout.addWidget(self.value_label)


        # Subtitle
        self.subtitle_label = None
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("cardSubtitle")
            self.subtitle_label.setFont(QFont("Segoe UI", 11))
            self.subtitle_label.setStyleSheet("color: #7f8c8d;")
            layout.addWidget(self.subtitle_label)
        else:
            # Create an empty subtitle label to update later if needed
            self.subtitle_label = QLabel("")
            self.subtitle_label.setObjectName("cardSubtitle")
            self.subtitle_label.setFont(QFont("Segoe UI", 11))
            self.subtitle_label.setStyleSheet("color: #7f8c8d;")
            self.subtitle_label.setVisible(False)
            layout.addWidget(self.subtitle_label)


        layout.addStretch()
        
    def set_clickable(self, clickable):
        """Set whether the card is clickable"""
        self._clickable = clickable
        if clickable:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            
    def set_on_click(self, callback):
        """Set a callback function to be called when the card is clicked"""
        self.clicked.connect(callback)
        
    def update_values(self, value, subtitle=None):
        """Update the card's value and subtitle dynamically"""
        # Always show a default value if value is None or empty
        if value is None or (isinstance(value, str) and value.strip() == ""):
            value = "0"
        self.value_label.setText(str(value))
        if subtitle and self.subtitle_label:
            self.subtitle_label.setText(str(subtitle))
            self.subtitle_label.setVisible(True)
        elif subtitle:
            # Create subtitle label if it doesn't exist
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("cardSubtitle")
            self.subtitle_label.setFont(QFont("Segoe UI", 11))
            self.subtitle_label.setStyleSheet("color: #7f8c8d;")
            self.layout().insertWidget(2, self.subtitle_label)
        elif self.subtitle_label:
            self.subtitle_label.setVisible(False)

    def mousePressEvent(self, event):
        """Handle mouse press events for clickable cards"""
        if self._clickable and event.button() == Qt.LeftButton:
            self._pressed = True
            self.setStyleSheet(self.pressed_stylesheet())
            super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for clickable cards"""
        if self._clickable and self._pressed and event.button() == Qt.LeftButton:
            self._pressed = False
            # Only emit clicked if the release is within the widget
            if self.rect().contains(event.pos()):
                self.clicked.emit()
            
            # Restore hover state if still hovering
            if self._hover:
                self.setStyleSheet(self.hover_stylesheet())
            else:
                self.setStyleSheet(self.default_stylesheet())
            
        super().mouseReleaseEvent(event)
            
    def enterEvent(self, event):
        """Handle mouse enter events for hover effects"""
        if self._clickable:
            self._hover = True
            self.setStyleSheet(self.hover_stylesheet())
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave events to remove hover effects"""
        if self._clickable:
            self._hover = False
            self._pressed = False
            self.setStyleSheet(self.default_stylesheet())
        super().leaveEvent(event)

    def default_stylesheet(self):
        return """
        QFrame#card {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        }


        QFrame#card:hover {
            border: 1px solid #3498db;
        }


        QLabel#cardTitle {
            color: #2c3e50;
        }


        QLabel#cardValue {
            color: #3498db;
            background-color: transparent;
        }


        QLabel#cardSubtitle {
            color: #7f8c8d;
        }
        """
        
    def hover_stylesheet(self):
        return """
        QFrame#card {
            background-color: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #3498db;
        }


        QLabel#cardTitle {
            color: #2c3e50;
        }


        QLabel#cardValue {
            color: #3498db;
        }


        QLabel#cardSubtitle {
            color: #7f8c8d;
        }
        """
        
    def pressed_stylesheet(self):
        return """
        QFrame#card {
            background-color: #ebf5fb;
            border-radius: 12px;
            border: 1px solid #2980b9;
        }


        QLabel#cardTitle {
            color: #2c3e50;
        }


        QLabel#cardValue {
            color: #2980b9;
        }


        QLabel#cardSubtitle {
            color: #7f8c8d;
        }
        """
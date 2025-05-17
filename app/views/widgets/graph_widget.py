from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsLineItem, QGraphicsTextItem,
    QGraphicsPathItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QCursor, QPen, QBrush, QPainterPath,
    QLinearGradient, QRadialGradient, QPainter
)
import random


class FlowChartItem:
    """Represents a flow chart node with connections"""
    def __init__(self, label, value, x, y, width=120, height=60, color="#3498db"):
        self.label = label
        self.value = value
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.connections = []  # List of other FlowChartItems this connects to
        
    def add_connection(self, other_item, label=""):
        """Connect this item to another item"""
        self.connections.append((other_item, label))


class GraphScene(QGraphicsScene):
    """Custom scene for rendering data visualizations"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set a semi-transparent background
        self.setBackgroundBrush(QColor(255, 255, 255, 30))
        
        # Create a background rectangle that covers the entire scene
        self.setSceneRect(0, 0, 360, 150)
        
    def drawBackground(self, painter, rect):
        """Override background drawing to add gradient effect"""
        super().drawBackground(painter, rect)
        
        # Draw a subtle gradient overlay
        gradient = QLinearGradient(0, 0, 0, 150)
        gradient.setColorAt(0, QColor(255, 255, 255, 15))
        gradient.setColorAt(1, QColor(0, 0, 0, 15))
        
        painter.fillRect(self.sceneRect(), gradient)
        
    def draw_flow_chart(self, items):
        """Draw a flow chart with the given items"""
        self.clear()
        
        # Background grid for orientation
        for x in range(0, 350, 50):
            grid_line = QGraphicsLineItem(x, 0, x, 150)
            grid_line.setPen(QPen(QColor(255, 255, 255, 20), 1, Qt.DashLine))
            self.addItem(grid_line)
            
        for y in range(0, 150, 50):
            grid_line = QGraphicsLineItem(0, y, 350, y)
            grid_line.setPen(QPen(QColor(255, 255, 255, 20), 1, Qt.DashLine))
            self.addItem(grid_line)
        
        # Draw connections first (so they appear behind nodes)
        for item in items:
            for connected_item, label in item.connections:
                # Draw the connection line
                path = QPainterPath()
                start_x = item.x + item.width/2
                start_y = item.y + item.height
                end_x = connected_item.x + connected_item.width/2
                end_y = connected_item.y
                
                # Create a curved path instead of straight line
                control_x = (start_x + end_x) / 2
                control_y = start_y + (end_y - start_y) / 2
                
                path.moveTo(start_x, start_y)
                path.quadTo(control_x, control_y, end_x, end_y)
                
                # Create the path item
                path_item = QGraphicsPathItem(path)
                path_item.setPen(QPen(QColor("#dddddd"), 2, Qt.SolidLine))
                self.addItem(path_item)
                
                # Add arrow at the end
                arrow_path = QPainterPath()
                arrow_x = end_x
                arrow_y = end_y
                arrow_path.moveTo(arrow_x, arrow_y)
                arrow_path.lineTo(arrow_x - 6, arrow_y - 12)
                arrow_path.lineTo(arrow_x + 6, arrow_y - 12)
                arrow_path.closeSubpath()
                
                arrow = QGraphicsPathItem(arrow_path)
                arrow.setBrush(QBrush(QColor("#dddddd")))
                arrow.setPen(QPen(QColor("#dddddd")))
                self.addItem(arrow)
                
                # Add connection label if any
                if label:
                    # Calculate position for label along the path
                    label_x = control_x - 20
                    label_y = control_y - 10
                    
                    # Create a background for better readability
                    label_bg = QGraphicsRectItem(0, 0, 0, 0)  # Will be sized based on text
                    label_bg.setBrush(QBrush(QColor(0, 0, 0, 80)))
                    label_bg.setPen(QPen(Qt.NoPen))
                    self.addItem(label_bg)
                    
                    # Add the text
                    text = QGraphicsTextItem(label)
                    text.setFont(QFont("Segoe UI", 8, QFont.Bold))
                    text.setDefaultTextColor(QColor("#ffffff"))
                    text.setPos(label_x, label_y)
                    
                    # Adjust background to fit text
                    rect = text.boundingRect()
                    padding = 4
                    label_bg.setRect(
                        label_x - padding,
                        label_y - padding,
                        rect.width() + padding * 2,
                        rect.height() + padding * 2
                    )
                    label_bg.setOpacity(0.5)
                    
                    self.addItem(text)
        
        # Draw nodes
        for item in items:
            # Create gradient for node background
            gradient = QLinearGradient(0, 0, 0, item.height)
            base_color = QColor(item.color)
            lighter_color = QColor(base_color)
            lighter_color.setAlpha(220)
            gradient.setColorAt(0, lighter_color)
            gradient.setColorAt(1, base_color)
            
            # Create drop shadow effect
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(
                item.x + 2, item.y + 2, item.width, item.height, 10, 10
            )
            shadow = QGraphicsPathItem(shadow_path)
            shadow.setBrush(QBrush(QColor(0, 0, 0, 40)))
            shadow.setPen(QPen(Qt.NoPen))
            self.addItem(shadow)
            
            # Create node path with rounded corners
            node_path = QPainterPath()
            node_path.addRoundedRect(
                item.x, item.y, item.width, item.height, 10, 10
            )
            
            # Create node shape
            rect = QGraphicsPathItem(node_path)
            rect.setBrush(QBrush(gradient))
            
            # Add a border with slight 3D effect
            border_pen = QPen(QColor(item.color).darker(120), 1)
            rect.setPen(border_pen)
            self.addItem(rect)
            
            # Add a highlight effect at the top
            highlight_path = QPainterPath()
            highlight_path.addRoundedRect(
                item.x + 2, item.y + 2, item.width - 4, 10, 5, 5
            )
            highlight = QGraphicsPathItem(highlight_path)
            highlight.setBrush(QBrush(QColor(255, 255, 255, 70)))
            highlight.setPen(QPen(Qt.NoPen))
            self.addItem(highlight)
            
            # Add label text
            label_text = QGraphicsTextItem(item.label)
            label_text.setFont(QFont("Segoe UI", 9, QFont.Bold))
            label_text.setDefaultTextColor(Qt.white)
            label_text.setPos(
                item.x + (item.width - label_text.boundingRect().width()) / 2,
                item.y + 5
            )
            self.addItem(label_text)
            
            # Add value text
            value_text = QGraphicsTextItem(str(item.value))
            value_text.setFont(QFont("Segoe UI", 14, QFont.Bold))
            value_text.setDefaultTextColor(Qt.white)
            value_text.setPos(
                item.x + (item.width - value_text.boundingRect().width()) / 2,
                item.y + item.height - value_text.boundingRect().height() - 5
            )
            self.addItem(value_text)
    
    def draw_bar_chart(self, data, title=""):
        """Draw a simple bar chart visualization"""
        self.clear()
        
        # Chart dimensions
        chart_width = 350
        chart_height = 120
        bar_spacing = 40
        max_bar_height = 100
        
        # Calculate the maximum value for scaling
        max_value = max([value for _, value in data]) if data else 1
        
        # Draw background grid
        for y in range(20, chart_height, 20):
            grid_line = QGraphicsLineItem(10, y + 10, chart_width + 10, y + 10)
            grid_line.setPen(QPen(QColor(255, 255, 255, 60), 1, Qt.DashLine))
            self.addItem(grid_line)
        
        # Draw axes
        x_axis = QGraphicsLineItem(10, chart_height + 10, chart_width + 10, chart_height + 10)
        x_axis.setPen(QPen(QColor(255, 255, 255, 180), 2))
        self.addItem(x_axis)
        
        y_axis = QGraphicsLineItem(10, 10, 10, chart_height + 10)
        y_axis.setPen(QPen(QColor(255, 255, 255, 180), 2))
        self.addItem(y_axis)
        
        # Draw value markers on y-axis
        y_values = [0, max_value/2, max_value]
        for i, value in enumerate(y_values):
            y_pos = chart_height + 10 - (i * chart_height/2)
            # Draw tick mark
            tick = QGraphicsLineItem(8, y_pos, 12, y_pos)
            tick.setPen(QPen(QColor(255, 255, 255, 180), 2))
            self.addItem(tick)
            # Draw value text
            value_text = QGraphicsTextItem(f"{int(value)}")
            value_text.setFont(QFont("Segoe UI", 8))
            value_text.setDefaultTextColor(QColor(255, 255, 255, 200))
            value_text.setPos(2, y_pos - 10)
            self.addItem(value_text)
        
        # Draw bars
        for i, (label, value) in enumerate(data):
            # Calculate bar dimensions
            bar_width = 30
            bar_height = (value / max_value) * max_bar_height if max_value > 0 else 0
            bar_x = 20 + i * bar_spacing
            bar_y = chart_height + 10 - bar_height
            
            # Create gradient
            gradient = QLinearGradient(0, bar_y, 0, chart_height + 10)
            color = QColor(random.choice(["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6"]))
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(1, color)
            
            # Draw highlight effect
            highlight = QGraphicsRectItem(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4)
            highlight.setBrush(QBrush())
            highlight.setPen(QPen(QColor(255, 255, 255, 60), 2))
            self.addItem(highlight)
            
            # Draw bar
            bar = QGraphicsRectItem(bar_x, bar_y, bar_width, bar_height)
            bar.setBrush(QBrush(gradient))
            bar.setPen(QPen(color.darker(110), 1))
            self.addItem(bar)
            
            # Add value on top of bar
            value_text = QGraphicsTextItem(str(int(value)))
            value_text.setFont(QFont("Segoe UI", 9, QFont.Bold))
            value_text.setDefaultTextColor(QColor(255, 255, 255))
            value_text.setPos(
                bar_x + (bar_width - value_text.boundingRect().width()) / 2,
                bar_y - 20
            )
            self.addItem(value_text)
            
            # Add label under bar
            label_text = QGraphicsTextItem(label)
            label_text.setFont(QFont("Segoe UI", 9))
            label_text.setDefaultTextColor(QColor(255, 255, 255))
            label_text.setPos(
                bar_x + (bar_width - label_text.boundingRect().width()) / 2,
                chart_height + 15
            )
            self.addItem(label_text)


class Graph(QFrame):
    # Define a signal that can be connected to
    clicked = pyqtSignal()
    
    def __init__(self, title, subtitle=None, color="#3498db", icon=None, clickable=True):
        super().__init__()
        self.setObjectName("graphCard")
        self.setMinimumHeight(200)
        
        # Store internal state
        self._clickable = clickable
        self._hover = False
        self._pressed = False
        self._color = color
        self._data = []
        self._chart_type = "bar"  # Default chart type
        
        # Make widget clickable if specified
        if clickable:
            self.setCursor(Qt.PointingHandCursor)

        # Set background color if provided
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
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Title row with icon
        title_layout = QHBoxLayout()
        if icon:
            self.icon_label = QLabel(icon)
            self.icon_label.setFont(QFont("Segoe UI", 16))
            title_layout.addWidget(self.icon_label)
        else:
            self.icon_label = None
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("graphTitle")
        font = QFont("Segoe UI", 12, QFont.Bold)
        self.title_label.setFont(font)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Create a graphics view for chart visualization
        self.scene = GraphScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 6px;
        """)
        self.view.setMinimumHeight(160)
        self.view.setFixedHeight(160)
        self.view.setFrameShape(QFrame.NoFrame)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Add default content to the scene
        if "Sales" in title:
            sample_data = [("Mon", 120), ("Tue", 150), ("Wed", 90), ("Thu", 200), ("Fri", 180)]
            self.scene.draw_bar_chart(sample_data)
            self._chart_type = "bar"
        elif "Stock" in title:
            flow_items = [
                FlowChartItem("Low Stock", "12", 20, 10, color="#f39c12"),
                FlowChartItem("Mid Stock", "24", 180, 10, color="#3498db"),
                FlowChartItem("Order", "5", 100, 100, color="#e74c3c")
            ]
            flow_items[0].add_connection(flow_items[2], "Place Order")
            flow_items[1].add_connection(flow_items[2], "Monitor")
            self.scene.draw_flow_chart(flow_items)
            self._chart_type = "flow"
        elif "Profit" in title:
            sample_data = [("Q1", 5000), ("Q2", 7500), ("Q3", 4000), ("Q4", 9000)]
            self.scene.draw_bar_chart(sample_data)
            self._chart_type = "bar"
            
        layout.addWidget(self.view)

        # Subtitle and indicators (if applicable)
        self.subtitle_layout = QHBoxLayout()
        self.subtitle_label = QLabel(subtitle or "")
        self.subtitle_label.setObjectName("graphSubtitle")
        self.subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 13px;")
        self.subtitle_layout.addWidget(self.subtitle_label)
        self.subtitle_layout.addStretch()

            # Add dynamic indicators
        self.indicator = QLabel("●")
        self.value_label = QLabel()
        self.value_label.setFont(QFont("Segoe UI", 13))

        if "Sales" in title:
            self.indicator.setStyleSheet("color: #27ae60;")
            self.value_label.setText("+15%")
        elif "Stock" in title:
            self.indicator.setStyleSheet("color: #e67e22;")
            self.value_label.setText("2 Stock Out")
        elif "Profit" in title:
            self.indicator.setStyleSheet("color: #e74c3c;")
            self.value_label.setText("-$300")

        self.subtitle_layout.addWidget(self.indicator)
        self.subtitle_layout.addWidget(self.value_label)
        layout.addLayout(self.subtitle_layout)

        # Apply appropriate styles
        self.update_style()
        
    def set_clickable(self, clickable):
        """Set whether the graph is clickable"""
        self._clickable = clickable
        if clickable:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def set_on_click(self, callback):
        """Set callback for click events"""
        self.clicked.connect(callback)
    
    def update_title(self, title):
        """Update the graph title"""
        self.title_label.setText(title)
        
    def update_subtitle(self, subtitle):
        """Update the graph subtitle"""
        self.subtitle_label.setText(subtitle)
        
    def update_indicator(self, value, color=None):
        """Update the indicator value and optionally its color"""
        self.value_label.setText(str(value))
        if color:
            self.indicator.setStyleSheet(f"color: {color};")
            
    def update_data(self, data):
        """Update the graph with new data visualization"""
        self._data = data
        
        if isinstance(data, str):
            # Simple text update (placeholder)
            return
            
        # If data is a list of tuples [(label, value), ...]
        if isinstance(data, list) and all(isinstance(item, tuple) and len(item) == 2 for item in data):
            if self._chart_type == "bar":
                self.scene.draw_bar_chart(data)
            
        # If data is for flow chart [{type: "node", ...}]
        elif isinstance(data, list) and all(isinstance(item, dict) and "type" in item for item in data):
            if self._chart_type == "flow":
                # Convert the dict data to FlowChartItem objects
                items = []
                for item_data in data:
                    if item_data["type"] == "node":
                        item = FlowChartItem(
                            item_data.get("label", ""),
                            item_data.get("value", ""),
                            item_data.get("x", 0),
                            item_data.get("y", 0),
                            item_data.get("width", 120),
                            item_data.get("height", 60),
                            item_data.get("color", "#3498db")
                        )
                        items.append(item)
                
                # Add connections
                for i, item_data in enumerate(data):
                    if "connections" in item_data:
                        for conn in item_data["connections"]:
                            if 0 <= conn["to"] < len(items):
                                items[i].add_connection(items[conn["to"]], conn.get("label", ""))
                
                self.scene.draw_flow_chart(items)
            
    def update_style(self):
        """Update the widget style based on current state"""
        if self._pressed:
            style = self.pressed_stylesheet()
        elif self._hover:
            style = self.hover_stylesheet()
        else:
            style = self.default_stylesheet()
        self.setStyleSheet(style)
            
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if self._clickable and event.button() == Qt.LeftButton:
            self._pressed = True
            self.update_style()
        super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if self._clickable and self._pressed and event.button() == Qt.LeftButton:
            self._pressed = False
            # Only emit clicked signal if release is within the widget
            if self.rect().contains(event.pos()):
                self.clicked.emit()
            
            # Restore appropriate style
            if self._hover:
                self._hover = True
            self.update_style()
        super().mouseReleaseEvent(event)
            
    def enterEvent(self, event):
        """Handle mouse enter events"""
        if self._clickable:
            self._hover = True
            self.update_style()
        super().enterEvent(event)
            
    def leaveEvent(self, event):
        """Handle mouse leave events"""
        if self._clickable:
            self._hover = False
            self._pressed = False
            self.update_style()
        super().leaveEvent(event)
            
    def default_stylesheet(self):
        return f"""
            QFrame#graphCard {{
                background-color: {self._color};
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }}
            QLabel#graphTitle {{
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }}
            QLabel#graphSubtitle {{
                color: rgba(255, 255, 255, 0.7);
                font-size: 13px;
            }}
        """
        
    def hover_stylesheet(self):
        return f"""
            QFrame#graphCard {{
                background-color: {self._color};
                border-radius: 12px;
                border: 1px solid #ffffff;
            }}
            QLabel#graphTitle {{
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }}
            QLabel#graphSubtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 13px;
            }}
        """
        
    def pressed_stylesheet(self):
        # Create a slightly darker version of the color
        return f"""
            QFrame#graphCard {{
                background-color: {self._color};
                border-radius: 12px;
                border: 2px solid #ffffff;
            }}
            QLabel#graphTitle {{
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }}
            QLabel#graphSubtitle {{
                color: #ffffff;
                font-size: 13px;
            }}
        """



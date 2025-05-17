"""
Smart Shop Manager - Enhanced Graph Widget
File: views/widgets/enhanced_graph.py
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect,
    QSizePolicy, QWidget, QSpacerItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette, QCursor, QPixmap, QPainter, QPen, QBrush, QPainterPath, QLinearGradient

# Import matplotlib for advanced charts
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
import random

# Set the style for matplotlib
plt.style.use('dark_background')


class ChartWidget(QWidget):
    """Custom widget for chart painting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None
        
    def paintEvent(self, event):
        """Paint the chart from the pixmap"""
        if self.pixmap:
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.pixmap)
            painter.end()
    
    def setPixmap(self, pixmap):
        """Set the pixmap to be painted"""
        self.pixmap = pixmap
        self.update()


class MplCanvas(FigureCanvas):
    """Matplotlib canvas for embedding in Qt widgets"""
    
    def __init__(self, width=5, height=4, dpi=100):
        # Set matplotlib style to light theme
        plt.style.use('seaborn-v0_8-whitegrid')
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#ffffff')
        self.axes = self.fig.add_subplot(111)
        
        # Customize the axes for light theme
        self.axes.set_facecolor('#ffffff')
        self.axes.tick_params(colors='#333333', which='both')
        for spine in self.axes.spines.values():
            spine.set_color('#e0e0e0')
        
        super(MplCanvas, self).__init__(self.fig)
        
        # Set canvas properties
        self.setStyleSheet("background: transparent;")
        
    def clear(self):
        """Clear the canvas and reset styling"""
        self.axes.clear()
        self.axes.set_facecolor('#ffffff')
        self.fig.patch.set_facecolor('#ffffff')
        for spine in self.axes.spines.values():
            spine.set_color('#e0e0e0')
        self.axes.tick_params(colors='#333333', which='both')


class EnhancedGraph(QFrame):
    """
    Enhanced graph widget with modern styling and interactive elements
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, title, subtitle="", chart_type='line', color="#3498db", icon="📊", parent=None):
        super().__init__(parent)
        self.setObjectName("enhanced-graph")
        
        # Set minimum size for better display
        self.setMinimumSize(320, 280)  # Increase minimum size for better visibility
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Store properties
        self.title = title
        self.subtitle = subtitle
        self.chart_type = chart_type
        self.color = color
        self.icon = icon
        self.data = None
        self.indicator_text = ""
        self.indicator_color = color
        # Add axis label attributes
        self.xlabel = ""
        self.ylabel = ""
        
        # Apply glass morphism styling
        self.setStyleSheet(f"""
            #enhanced-graph {{
                background-color: #f8f9fa;
                border-radius: 18px;
                border: 1px solid rgba(0, 0, 0, 0.1);
                padding: 8px;
            }}
            #enhanced-graph:hover {{
                background-color: #f8f9fa;
                border: 1px solid rgba(0, 0, 0, 0.2);
            }}
            QLabel#graph-title {{
                color: #333333;
                font-size: 18px;
                font-weight: bold;
                padding: 0;
            }}
            QLabel#graph-subtitle {{
                color: rgba(0, 0, 0, 0.7);
                font-size: 13px;
            }}
            QLabel#graph-indicator {{
                color: {color};
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }}
            QLabel#graph-icon {{
                font-size: 20px;
                color: white;
                background-color: {color};
                border-radius: 15px;
                padding: 5px;
            }}
        """)
            
        # Set cursor to pointing hand to indicate clickable
        self.setCursor(Qt.PointingHandCursor)
        
        # Add drop shadow for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)
        
        # Initialize the UI components
        self._init_ui()
        
        # Generate random data for initial display
        self._generate_placeholder_data()
        
    def _init_ui(self):
        """Initialize all UI components"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(22, 22, 22, 22)
        self.layout.setSpacing(10)
        
        # Header layout with title and icon
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Icon container
        self.icon_label = QLabel(self.icon)
        self.icon_label.setObjectName("graph-icon")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(38, 38)
        header_layout.addWidget(self.icon_label)
        
        # Title container
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("graph-title")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #222; background: transparent;")
        title_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel(self.subtitle)
        self.subtitle_label.setObjectName("graph-subtitle")
        self.subtitle_label.setStyleSheet("font-size: 13px; color: #888; font-weight: 400; background: transparent;")
        title_layout.addWidget(self.subtitle_label)
        
        header_layout.addLayout(title_layout, 1)
        
        # KPI indicator label
        self.indicator_label = QLabel()
        self.indicator_label.setObjectName("graph-indicator")
        self.indicator_label.setFixedHeight(38)
        self.indicator_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.indicator_label)
        
        self.layout.addLayout(header_layout)
        
        # Subtle divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Plain)
        divider.setStyleSheet("color: #e0e0e0; background: #e0e0e0; min-height: 2px; max-height: 2px; border: none;")
        self.layout.addWidget(divider)
        
        # Chart area - use MplCanvas for line chart, ChartWidget for others
        if self.chart_type == 'line':
            self.mpl_canvas = MplCanvas(width=5, height=2.2, dpi=100)
            self.mpl_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout.addWidget(self.mpl_canvas)
        else:
            self.chart_area = ChartWidget()
            self.chart_area.setObjectName("chart-area")
            self.chart_area.setMinimumHeight(180)
            self.chart_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.chart_area.setStyleSheet("""
                #chart-area {
                    background-color: rgba(0, 0, 0, 0.05);
                    border-radius: 14px;
                    border: 1px solid rgba(0, 0, 0, 0.05);
                }
            """)
            self.layout.addWidget(self.chart_area)
        # Ensure vertical centering
        self.layout.addStretch()
        self.setMinimumHeight(320)
        self.setMaximumHeight(340)
        
    def _generate_placeholder_data(self):
        """Generate placeholder data based on chart type"""
        if self.chart_type == 'line':
            # For line chart: 7 days of data
            labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            data = [random.randint(30, 100) for _ in range(7)]
            
            self.data = {
                "labels": labels,
                "data": data
            }
            
        elif self.chart_type == 'bar':
            # For bar chart: Quarterly data
            labels = ["Q1", "Q2", "Q3", "Q4"]
            data = [random.randint(5000, 10000) for _ in range(4)]
            
            self.data = {
                "labels": labels,
                "data": data
            }
            
        elif self.chart_type == 'flow':
            # For flow chart: Generate nodes and connections
            self.data = [
                {"type": "node", "label": "Inventory", "value": "45", "x": 50, "y": 50, "color": "#3498db"},
                {"type": "node", "label": "Sales", "value": "28", "x": 200, "y": 50, "color": "#2ecc71"},
                {"type": "node", "label": "Suppliers", "value": "12", "x": 50, "y": 150, "color": "#f39c12"},
                {"type": "node", "label": "Customers", "value": "60", "x": 200, "y": 150, "color": "#9b59b6"}
            ]
            
            # Add connections between nodes
            self.data[0]["connections"] = [{"to": 1, "label": "Out"}]
            self.data[2]["connections"] = [{"to": 0, "label": "In"}]
            self.data[1]["connections"] = [{"to": 3, "label": "Sold"}]
        
    def paintEvent(self, event):
        """Custom paint event to draw the chart"""
        super().paintEvent(event)
        if self.chart_type == 'line' and hasattr(self, 'mpl_canvas') and self.data:
            self._draw_matplotlib_line_chart()
        elif self.data and hasattr(self, 'chart_area'):
            # Existing QPainter logic for bar/flow
            pixmap = QPixmap(self.chart_area.size())
            pixmap.fill(QColor(0, 0, 0, 0))
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            chart_width = self.chart_area.width()
            chart_height = self.chart_area.height()
            padding = 15
            if self.chart_type == 'bar':
                self._draw_bar_chart(painter, chart_width, chart_height, padding)
            elif self.chart_type == 'flow':
                self._draw_flow_chart(painter, chart_width, chart_height)
            painter.end()
            self.chart_area.setPixmap(pixmap)
        
    def _draw_matplotlib_line_chart(self):
        """Draw a modern, visually appealing line chart using Matplotlib."""
        if not hasattr(self, 'mpl_canvas'):
            return
            
        self.mpl_canvas.clear()
        
        # Handle data format conversion
        if isinstance(self.data, dict) and 'data' in self.data:
            # Convert old format to new format
            x = self.data.get('labels', list(range(len(self.data['data']))))
            y = self.data['data']
            data = [{'x': x, 'y': y, 'label': self.title}]
        else:
            data = self.data if isinstance(self.data, list) else [self.data]
            
        if not data or not any(series.get('y') for series in data):
            return
            
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']  # Modern palette
        line_styles = ['-', '--', '-.', ':']

        for idx, series in enumerate(data):
            x = series.get('x', [])
            y = series.get('y', [])
            if not x or not y:
                continue
                
            label = series.get('label', f"Series {idx+1}")
            color = colors[idx % len(colors)]
            style = line_styles[idx % len(line_styles)]
            
            # Plot with improved styling
            self.mpl_canvas.axes.plot(
                x, y,
                linestyle=style,
                linewidth=2.5,
                color=color,
                marker='o',
                markersize=7,
                markerfacecolor=color,
                markeredgecolor='white',
                markeredgewidth=2,
                label=label,
                antialiased=True,
                zorder=3
            )
            
            # Add subtle gradient fill
            self.mpl_canvas.axes.fill_between(
                x, y,
                alpha=0.1,
                color=color,
                zorder=2
            )

        # Title and subtitle
        self.mpl_canvas.axes.set_title(
            self.title or "Performance Chart",
            fontsize=15,
            fontweight='bold',
            color='#222',
            pad=16,
            fontfamily='Segoe UI'
        )
        
        if hasattr(self, 'subtitle') and self.subtitle:
            self.mpl_canvas.axes.text(
                0.5, 1.04,
                self.subtitle,
                transform=self.mpl_canvas.axes.transAxes,
                ha='center',
                va='bottom',
                fontsize=11,
                color='#666',
                alpha=0.85,
                fontfamily='Segoe UI'
            )

        # Axis labels with improved styling
        self.mpl_canvas.axes.set_xlabel(
            self.xlabel or '',
            fontsize=13,
            fontfamily='Segoe UI',
            color='#222',
            labelpad=10
        )
        self.mpl_canvas.axes.set_ylabel(
            self.ylabel or '',
            fontsize=13,
            fontfamily='Segoe UI',
            color='#222',
            labelpad=10
        )

        # Ticks with improved styling
        self.mpl_canvas.axes.tick_params(
            axis='both',
            which='major',
            labelsize=11,
            colors='#444',
            labelrotation=0
        )
        
        # Set font for all text elements
        for label in self.mpl_canvas.axes.get_xticklabels() + self.mpl_canvas.axes.get_yticklabels():
            label.set_fontfamily('Segoe UI')

        # Dynamic Y range with padding
        all_y = []
        for series in data:
            all_y.extend(series.get('y', []))
        if all_y:
            ymin = min(all_y)
            ymax = max(all_y)
            yrange = ymax - ymin
            padding = 0.1 * yrange if yrange else 1
            self.mpl_canvas.axes.set_ylim(
                ymin - padding,
                ymax + padding
            )

        # Grid with improved styling
        self.mpl_canvas.axes.grid(
            True,
            which='major',
            axis='both',
            linestyle='--',
            linewidth=1,
            color='#bbb',
            alpha=0.25,
            zorder=1
        )

        # Legend with improved styling
        if len(data) > 1:
            self.mpl_canvas.axes.legend(
                loc='upper right',
                fontsize=11,
                frameon=False,
                labelcolor='#222',
                fontfamily='Segoe UI'
            )

        # Remove top/right spines for modern look
        self.mpl_canvas.axes.spines['top'].set_visible(False)
        self.mpl_canvas.axes.spines['right'].set_visible(False)
        self.mpl_canvas.axes.spines['left'].set_color('#e0e0e0')
        self.mpl_canvas.axes.spines['bottom'].set_color('#e0e0e0')

        # Ensure white background
        self.mpl_canvas.figure.set_facecolor('#ffffff')
        self.mpl_canvas.axes.set_facecolor('#ffffff')
        
        # Adjust layout
        self.mpl_canvas.figure.subplots_adjust(
            left=0.13,
            right=0.97,
            top=0.85,
            bottom=0.18
        )

        self.mpl_canvas.draw()
    
    def _draw_bar_chart(self, painter, width, height, padding):
        """Draw a bar chart with the provided data"""
        if not self.data or "data" not in self.data or not self.data["data"]:
            return
            
        # Extract data
        data_values = self.data["data"]
        labels = self.data.get("labels", [])
        
        # Find max value for scaling
        max_value = max(data_values) * 1.1 if data_values else 0  # Add 10% padding at the top
        
        # Calculate drawing dimensions
        draw_width = width - 2 * padding
        draw_height = height - 2 * padding
        
        # Draw bottom axis with subtle styling
        painter.setPen(QPen(QColor(100, 100, 100, 80), 1))
        painter.drawLine(padding, height - padding, width - padding, height - padding)
        
        # If no data values, exit
        if not data_values:
            return
            
        # Calculate bar width and spacing with improved proportions
        num_bars = len(data_values)
        bar_spacing = draw_width / (num_bars * 3)  # Adjusted for better spacing
        bar_width = draw_width / num_bars - bar_spacing
        
        # Draw grid lines with subtle styling
        painter.setPen(QPen(QColor(100, 100, 100, 40), 1, Qt.DotLine))
        
        # Horizontal grid lines with improved appearance
        num_horizontal_lines = 5
        for i in range(1, num_horizontal_lines + 1):
            # Convert float y position to int to fix the type error
            y = int(height - padding - (i * draw_height / num_horizontal_lines))
            painter.drawLine(padding, y, width - padding, y)
            
            # Draw y-axis labels with improved formatting
            value = i * max_value / num_horizontal_lines
            painter.setPen(QPen(QColor(200, 200, 200, 130), 1))
            
            # Format based on value size
            if value >= 1000:
                value_text = f"${value/1000:.1f}K"
            else:
                value_text = f"${value:.0f}"
            
            # Properly align y-axis labels
            label_width = painter.fontMetrics().horizontalAdvance(value_text)    
            painter.drawText(int(padding - label_width - 5), y + 4, value_text)
            
        # Draw bars with modern styling and gradients
        for i, value in enumerate(data_values):
            # Calculate bar position - convert to int
            x = int(padding + i * (bar_width + bar_spacing) + bar_spacing / 2)
            
            # Calculate bar height - convert to int
            ratio = value / max_value if max_value > 0 else 0
            bar_height = int(ratio * draw_height)
            
            # Create gradient for bar with enhanced colors
            base_color = QColor(self.color)
            gradient = QLinearGradient(x, height - padding - bar_height, x, height - padding)
            gradient.setColorAt(0, base_color.lighter(120))  # Lighter at top
            gradient.setColorAt(1, base_color)               # Original at bottom
            
            # Define gradient points
            y_top = int(height - padding - bar_height)
            y_bottom = int(height - padding)
            
            # Draw bar with rounded top corners and improved appearance
            path = QPainterPath()
            path.moveTo(x, y_bottom)  # Bottom left
            path.lineTo(x, y_top + 8)  # Near top left with space for radius
            path.arcTo(int(x), int(y_top), 16, 16, 180, 90)  # Top left corner
            path.lineTo(x + int(bar_width) - 8, y_top)  # Top edge
            path.arcTo(int(x + bar_width - 16), int(y_top), 16, 16, 270, 90)  # Top right corner
            path.lineTo(x + int(bar_width), y_bottom)  # Bottom right
            path.closeSubpath()
            
            # Fill the bar with gradient
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawPath(path)
            
            # Add gloss effect (subtle highlight on top)
            highlight_path = QPainterPath()
            highlight_path.moveTo(int(x + 3), int(y_top + 8))
            highlight_path.lineTo(int(x + 3), int(y_top + bar_height * 0.25))
            highlight_path.lineTo(int(x + bar_width - 3), int(y_top + bar_height * 0.25))
            highlight_path.lineTo(int(x + bar_width - 3), int(y_top + 8))
            highlight_path.closeSubpath()
            
            # Apply semi-transparent white for glossy effect
            highlight_color = QColor(255, 255, 255, 50)
            painter.setBrush(QBrush(highlight_color))
            painter.drawPath(highlight_path)
            
            # Add subtle shadow at bottom for depth
            shadow_path = QPainterPath()
            shadow_path.moveTo(int(x), int(y_bottom - 2))
            shadow_path.lineTo(int(x + bar_width), int(y_bottom - 2))
            shadow_path.lineTo(int(x + bar_width + 4), int(y_bottom + 2))
            shadow_path.lineTo(int(x - 4), int(y_bottom + 2))
            shadow_path.closeSubpath()
            
            shadow_color = QColor(0, 0, 0, 30)
            painter.setBrush(QBrush(shadow_color))
            painter.drawPath(shadow_path)
            
            # Draw value at the top of the bar with improved styling
            painter.setPen(QPen(QColor(255, 255, 255, 230), 1))
            # Format value text with K for thousands
            if value >= 1000:
                value_text = f"${value/1000:.1f}K"
            else:
                value_text = f"${value:.0f}"
                
            text_width = painter.fontMetrics().horizontalAdvance(value_text)
            text_y = int(y_top - 10)  # Position text above the bar with more padding
            bar_center_x = int(x + bar_width / 2)
            painter.drawText(int(bar_center_x - text_width / 2), text_y, value_text)
            
            # Draw x-axis labels with improved styling
            if i < len(labels):
                painter.setPen(QPen(QColor(255, 255, 255, 230), 1))
                text_width = painter.fontMetrics().horizontalAdvance(labels[i])
                painter.drawText(int(bar_center_x - text_width / 2), int(height - padding + 15), labels[i])
    
    def _draw_flow_chart(self, painter, width, height):
        """Draw a flow chart with nodes and connections"""
        if not self.data:
            return
            
        # Set up painter
        painter.setPen(QPen(QColor(200, 200, 200, 150), 1))
        
        # Draw all connections first (so they appear behind nodes)
        for node in self.data:
            if "connections" in node:
                source_x = int(node.get("x", 0))
                source_y = int(node.get("y", 0))
                
                for connection in node["connections"]:
                    target_idx = connection.get("to", 0)
                    if target_idx < len(self.data):
                        target = self.data[target_idx]
                        target_x = int(target.get("x", 0))
                        target_y = int(target.get("y", 0))
                        
                        # Calculate control points for curve
                        if source_x < target_x:
                            # Source is to the left of target
                            cp1x = int(source_x + (target_x - source_x) * 0.7)
                            cp1y = int(source_y)
                            cp2x = int(target_x - (target_x - source_x) * 0.7)
                            cp2y = int(target_y)
                        else:
                            # Source is to the right of target (curve needs to go around)
                            cp1x = int(source_x + 20)
                            cp1y = int(source_y - 50)
                            cp2x = int(target_x - 20)
                            cp2y = int(target_y - 50)
                        
                        # Draw arrow path
                        path = QPainterPath()
                        path.moveTo(source_x, source_y)
                        path.cubicTo(cp1x, cp1y, cp2x, cp2y, target_x, target_y)
                        
                        # Create gradient for arrow
                        source_color = QColor(node.get("color", self.color))
                        target_color = QColor(target.get("color", self.color))
                        
                        # Draw the path with gradient and increased width
                        pen = QPen(source_color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                        painter.setPen(pen)
                        painter.drawPath(path)
                        
                        # Add arrow head
                        arrow_size = 8
                        # Calculate angle at the end of the curve
                        angle = np.arctan2(target_y - cp2y, target_x - cp2x)
                        
                        # Calculate arrow points
                        arrow_p1_x = int(target_x - arrow_size * np.cos(angle - np.pi/6))
                        arrow_p1_y = int(target_y - arrow_size * np.sin(angle - np.pi/6))
                        arrow_p2_x = int(target_x - arrow_size * np.cos(angle + np.pi/6))
                        arrow_p2_y = int(target_y - arrow_size * np.sin(angle + np.pi/6))
                        
                        # Draw arrow head
                        arrow_path = QPainterPath()
                        arrow_path.moveTo(target_x, target_y)
                        arrow_path.lineTo(arrow_p1_x, arrow_p1_y)
                        arrow_path.lineTo(arrow_p2_x, arrow_p2_y)
                        arrow_path.closeSubpath()
                        
                        painter.setBrush(QBrush(target_color))
                        painter.setPen(Qt.NoPen)
                        painter.drawPath(arrow_path)
                        
                        # Draw connection label
                        label = connection.get("label", "")
                        if label:
                            mid_x = int((source_x + target_x) / 2)
                            mid_y = int((source_y + target_y) / 2)
                            
                            # Adjust position based on curve
                            if source_x < target_x:
                                label_x = mid_x
                                label_y = mid_y - 10
                            else:
                                label_x = mid_x
                                label_y = mid_y - 30
                            
                            # Draw label background
                            label_width = int(painter.fontMetrics().horizontalAdvance(label) + 10)
                            label_height = int(painter.fontMetrics().height() + 4)
                            
                            painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
                            painter.setPen(Qt.NoPen)
                            painter.drawRoundedRect(
                                int(label_x - label_width / 2),
                                int(label_y - label_height / 2),
                                label_width,
                                label_height,
                                5, 5
                            )
                            
                            # Draw label text
                            painter.setPen(QPen(QColor(255, 255, 255, 200), 1))
                            painter.drawText(
                                int(label_x - label_width / 2 + 5),
                                int(label_y + label_height / 4),
                                label
                            )
        
        # Draw all nodes
        for node in self.data:
            if node.get("type", "") == "node":
                x = int(node.get("x", 0))
                y = int(node.get("y", 0))
                label = node.get("label", "")
                value = node.get("value", "")
                color = node.get("color", self.color)
                
                # Draw node background
                node_color = QColor(color)
                node_width = 80
                node_height = 40
                
                # Draw main body
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(node_color))
                painter.drawRoundedRect(
                    int(x - node_width / 2),
                    int(y - node_height / 2),
                    node_width,
                    node_height,
                    10, 10
                )
                
                # Add gloss effect
                highlight_color = QColor(255, 255, 255, 40)
                painter.setBrush(QBrush(highlight_color))
                painter.drawRoundedRect(
                    int(x - node_width / 2 + 2),
                    int(y - node_height / 2 + 2),
                    int(node_width - 4),
                    int(node_height / 2 - 4),
                    8, 8
                )
                
                # Draw labels with proper centering
                painter.setPen(QPen(QColor(255, 255, 255, 230), 1))
                
                # Center-align label
                label_width = painter.fontMetrics().horizontalAdvance(label)
                label_x = int(x - label_width / 2)
                painter.drawText(
                    label_x,
                    int(y - node_height / 4),
                    label
                )
                
                # Center-align value
                value_width = painter.fontMetrics().horizontalAdvance(value)
                value_x = int(x - value_width / 2)
                painter.setPen(QPen(QColor(255, 255, 255, 230), 1))
                painter.drawText(
                    value_x,
                    int(y + node_height / 4),
                    value
                )
    
    def update_data(self, new_data):
        """Update the chart data and repaint"""
        self.data = new_data
        if self.chart_type == 'line' and hasattr(self, 'mpl_canvas'):
            self._draw_matplotlib_line_chart()
        elif hasattr(self, 'chart_area'):
            self.chart_area.update()
    
    def update_title(self, new_title):
        """Update the chart title"""
        self.title = new_title
        self.title_label.setText(new_title)
    
    def update_subtitle(self, new_subtitle):
        """Update the chart subtitle"""
        self.subtitle = new_subtitle
        self.subtitle_label.setText(new_subtitle)
    
    def update_indicator(self, text, color=None):
        """Update the indicator text and color"""
        self.indicator_text = text
        self.indicator_label.setText(text)
        
        if color:
            self.indicator_color = color
            self.indicator_label.setStyleSheet(f"""
                QLabel#graph-indicator {{
                    color: {color};
                    font-size: 16px;
                    font-weight: bold;
                    padding: 8px;
                    background-color: rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                }}
            """)
            
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        self.clicked.emit()
        super().mousePressEvent(event)
            
    def set_on_click(self, callback):
        """Set callback function for click events"""
        self.clicked.connect(callback) 
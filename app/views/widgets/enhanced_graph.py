"""
Smart Shop Manager - Enhanced Graph Widget
File: views/widgets/enhanced_graph.py
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QRectF, QPointF
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPainterPath, QLinearGradient
from datetime import datetime, timedelta

class ChartWidget(QWidget):
    """Custom widget for painting charts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(220)
        self.setMaximumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.data = []
        self.labels = []
        self.chart_type = 'line'
        self.color = '#3498db'
        self.setStyleSheet("")

    def set_data(self, data, labels=None, chart_type='line', color='#3498db'):
        # Convert dictionary data to list of values if needed
        if isinstance(data, dict):
            self.data = list(data.values())
            self.labels = list(data.keys()) if labels is None else labels
        else:
            self.data = data
            self.labels = labels or [str(i) for i in range(len(data))]
            
        # Ensure data is numeric
        try:
            self.data = [float(x) if x is not None else 0.0 for x in self.data]
        except (ValueError, TypeError):
            print("Warning: Non-numeric data points will be converted to 0")
            self.data = [0.0 if not isinstance(x, (int, float)) else float(x) for x in self.data]
            
        self.chart_type = chart_type
        self.color = color
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        # Rounded chart area
        chart_rect = QRectF(8, 8, width-16, height-16)
        path = QPainterPath()
        path.addRoundedRect(chart_rect, 18, 18)
        painter.setClipPath(path)
        # Subtle gradient background
        grad = QLinearGradient(0, 0, 0, height)
        grad.setColorAt(0, QColor('#f8fbff'))
        grad.setColorAt(1, QColor('#eaf6fb'))
        painter.fillRect(self.rect(), grad)
        # Validate data
        if not self.data:
            return
        data_values = self.data
        # More padding for better visuals
        margin_left = 60
        margin_right = 30
        margin_top = 30
        margin_bottom = 40
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        min_val = min(data_values)
        max_val = max(data_values)
        range_val = max_val - min_val
        if range_val == 0:
            range_val = 1
        padding = range_val * 0.1
        min_val -= padding
        max_val += padding
        range_val = max_val - min_val
        # Draw lighter, thinner grid lines
        grid_pen = QPen(QColor('#e8eef3'), 1, Qt.DashLine)
        painter.setPen(grid_pen)
        for i in range(5):
            y = int(height - margin_bottom - (i * chart_height / 4))
            painter.drawLine(int(margin_left), y, int(width - margin_right), y)
        # Draw axes (bolder, darker)
        axis_pen = QPen(QColor('#455a64'), 2)
        painter.setPen(axis_pen)
        painter.drawLine(int(margin_left), int(height - margin_bottom), int(width - margin_right), int(height - margin_bottom))
        painter.drawLine(int(margin_left), int(margin_top), int(margin_left), int(height - margin_bottom))
        # Draw chart
        if self.chart_type == 'line':
            self._draw_line_chart(painter, margin_left, chart_width, chart_height, min_val, range_val, margin_top, margin_bottom, data_values)
        elif self.chart_type == 'bar':
            self._draw_bar_chart(painter, margin_left, chart_width, chart_height, min_val, range_val, margin_top, margin_bottom, data_values)
        # Draw labels
        self._draw_labels(painter, margin_left, chart_width, chart_height, margin_top, margin_bottom, data_values)

    def _draw_line_chart(self, painter, margin_left, chart_width, chart_height, min_val, range_val, margin_top, margin_bottom, data_values):
        path = QPainterPath()
        n = len(data_values)
        point_color = QColor('#00b894')  # Vibrant green
        line_color = QColor('#0984e3')   # Vibrant blue
        painter.setPen(QPen(line_color, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for i, value in enumerate(data_values):
            x = margin_left + (i * chart_width / (n - 1))
            y = self.height() - margin_bottom - ((value - min_val) * chart_height / range_val)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        painter.drawPath(path)
        # Draw larger, vibrant points with drop shadow and value labels
        for i, value in enumerate(data_values):
            x = margin_left + (i * chart_width / (n - 1))
            y = self.height() - margin_bottom - ((value - min_val) * chart_height / range_val)
            # Drop shadow
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 40))
            painter.drawEllipse(QPointF(x+2, y+4), 8, 8)
            # Main point
            painter.setPen(QPen(point_color, 2))
            painter.setBrush(QBrush(point_color))
            painter.drawEllipse(QPointF(x, y), 7, 7)
            # Value label (above or below point, clipped)
            label_y = y - 22 if y - 22 > margin_top + 2 else y + 22
            self._draw_value_label(painter, x, label_y, f'{value:.0f}')

    def _draw_bar_chart(self, painter, margin_left, chart_width, chart_height, min_val, range_val, margin_top, margin_bottom, data_values):
        n = len(data_values)
        if n == 0:
            return  # Nothing to draw
        if n == 1:
            bar_width = chart_width / 2
            bar_color = QColor('#6c5ce7')
            value = data_values[0]
            x = margin_left + chart_width / 2 - bar_width / 2
            y = self.height() - margin_bottom - ((value - min_val) * chart_height / range_val)
            bar_height = self.height() - margin_bottom - y
            painter.setPen(Qt.NoPen)
            shadow_color = QColor(bar_color)
            shadow_color.setAlpha(50)
            painter.setBrush(QBrush(shadow_color))
            painter.drawRoundedRect(QRectF(x+2, y+8, bar_width, bar_height), 6, 6)
            grad = QLinearGradient(x, y, x, y+bar_height)
            grad.setColorAt(0, bar_color.lighter(120))
            grad.setColorAt(1, bar_color.darker(120))
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(QRectF(x, y, bar_width, bar_height), 6, 6)
            label_y = y - 24 if y - 24 > margin_top + 2 else y + 22
            font = QFont('Segoe UI', 10, QFont.Bold)
            painter.setFont(font)
            outline_pen = QPen(QColor('#fff'), 4)
            painter.setPen(outline_pen)
            painter.drawText(QRectF(x, label_y, bar_width, 20), Qt.AlignCenter, f'{value:.0f}')
            painter.setPen(QPen(QColor('#222'), 1))
            painter.drawText(QRectF(x, label_y, bar_width, 20), Qt.AlignCenter, f'{value:.0f}')
            return
        bar_width = chart_width / (n * 1.5)
        bar_color = QColor('#6c5ce7')  # Vibrant purple
        for i, value in enumerate(data_values):
            x = margin_left + (i * chart_width / (n - 1)) - bar_width / 2
            y = self.height() - margin_bottom - ((value - min_val) * chart_height / range_val)
            bar_height = self.height() - margin_bottom - y
            # Drop shadow
            painter.setPen(Qt.NoPen)
            shadow_color = QColor(bar_color)
            shadow_color.setAlpha(50)
            painter.setBrush(QBrush(shadow_color))
            painter.drawRoundedRect(QRectF(x+2, y+8, bar_width, bar_height), 6, 6)
            # Gradient fill
            grad = QLinearGradient(x, y, x, y+bar_height)
            grad.setColorAt(0, bar_color.lighter(120))
            grad.setColorAt(1, bar_color.darker(120))
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(QRectF(x, y, bar_width, bar_height), 6, 6)
            # Value label (above bar, always visible)
            label_y = y - 24 if y - 24 > margin_top + 2 else y + 22
            # Draw white outline for contrast
            font = QFont('Segoe UI', 10, QFont.Bold)
            painter.setFont(font)
            outline_pen = QPen(QColor('#fff'), 4)
            painter.setPen(outline_pen)
            painter.drawText(QRectF(x, label_y, bar_width, 20), Qt.AlignCenter, f'{value:.0f}')
            # Draw main text
            painter.setPen(QPen(QColor('#222'), 1))
            painter.drawText(QRectF(x, label_y, bar_width, 20), Qt.AlignCenter, f'{value:.0f}')

    def _draw_value_label(self, painter, x, y, text):
        # Draw white outline for contrast
        font = QFont('Segoe UI', 10, QFont.Bold)
        painter.setFont(font)
        outline_pen = QPen(QColor('#fff'), 4)
        painter.setPen(outline_pen)
        painter.drawText(QRectF(x-25, y-15, 50, 20), Qt.AlignCenter, text)
        # Draw main text
        painter.setPen(QPen(QColor('#222'), 1))
        painter.drawText(QRectF(x-25, y-15, 50, 20), Qt.AlignCenter, text)

    def _draw_labels(self, painter, margin_left, chart_width, chart_height, margin_top, margin_bottom, data_values):
        painter.setPen(QPen(QColor('#333'), 1))
        painter.setFont(QFont('Segoe UI', 9, QFont.Bold))
        n = len(self.labels)
        # Draw x-axis labels
        for i, label in enumerate(self.labels):
            x = margin_left + (i * chart_width / (n - 1))
            y = self.height() - margin_bottom + 24
            painter.drawText(QRectF(x - 30, y, 60, 20), Qt.AlignCenter, str(label))
        # Draw y-axis labels
        for i in range(5):
            y = self.height() - margin_bottom - (i * chart_height / 4)
            value = min(data_values) + (i * (max(data_values) - min(data_values)) / 4)
            painter.drawText(QRectF(0, y - 10, margin_left - 8, 20), Qt.AlignRight | Qt.AlignVCenter, f'{value:.1f}')

class EnhancedGraph(QFrame):
    """Enhanced graph widget with modern styling and interactive elements"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("enhancedGraph")
        self._hover = False
        self.setStyleSheet(self.default_stylesheet())
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(8)
        # Active (main) label
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            background-color: #fff;
            color: #111;
            border-radius: 16px;
            padding: 6px 18px;
            font-weight: bold;
            font-size: 15px;
            border: 1px solid #e0e0e0;
        """)
        self.header_layout.addWidget(self.title_label)
        # Inactive (subtitle) label
        self.subtitle_label = QLabel()
        self.subtitle_label.setStyleSheet("""
            background-color: #fff;
            color: #4a6a7a;
            border-radius: 16px;
            padding: 6px 18px;
            font-weight: normal;
            font-size: 15px;
            border: 1px solid #e0e0e0;
        """)
        self.header_layout.addWidget(self.subtitle_label)
        self.header_layout.addStretch()
        self.indicator_label = QLabel()
        self.indicator_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            padding: 2px 10px;
            border-radius: 8px;
            background: #f0f0f0;
            color: #333333;
        """)
        self.header_layout.addWidget(self.indicator_label)
        self.layout.addLayout(self.header_layout)
        self.chart = ChartWidget()
        self.layout.addWidget(self.chart)
        self.indicator_label.hide()
        self.click_callback = None

    def enterEvent(self, event):
        self._hover = True
        self.setStyleSheet(self.hover_stylesheet())
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.setStyleSheet(self.default_stylesheet())
        super().leaveEvent(event)

    def default_stylesheet(self):
        return """
        #enhancedGraph {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1.5px solid rgba(0, 0, 0, 0.08);
        }
        """

    def hover_stylesheet(self):
        return """
        #enhancedGraph {
            background-color: #fafdff;
            border-radius: 12px;
            border: 2px solid #4fc3f7;
        }
        """

    def set_title(self, title, subtitle=None):
        self.title_label.setText(title)
        if subtitle:
            self.subtitle_label.setText(subtitle)
        else:
            self.subtitle_label.setText("")

    def set_data(self, data, labels=None, chart_type='line', color='#3498db'):
        self.chart.set_data(data, labels, chart_type, color)
        
    def update_data(self, data, labels=None, chart_type=None, color=None):
        """Update the graph data with new values"""
        if chart_type is None:
            chart_type = self.chart.chart_type
        if color is None:
            color = self.chart.color
        self.set_data(data, labels, chart_type, color)
    
    def update_indicator(self, text, color=None):
        self.indicator_label.setText(text)
        if color:
            self.indicator_label.setStyleSheet(f"font-size: 13px; font-weight: bold; padding: 2px 10px; border-radius: 8px; background: {color}; color: #fff;")
        self.indicator_label.show()

    def set_on_click(self, callback):
        self.click_callback = callback
            
    def mousePressEvent(self, event):
        # Show Plotly chart in the default web browser
        try:
            import plotly.graph_objs as go
            import plotly.io as pio
            import webbrowser
            import tempfile
            import os
            title = self.title_label.text()
            data = self.chart.data
            labels = self.chart.labels
            chart_type = self.chart.chart_type
            color = self.chart.color
            if chart_type == 'bar':
                fig = go.Figure([go.Bar(x=labels, y=data, marker_color=color)])
            else:
                fig = go.Figure([go.Scatter(x=labels, y=data, mode='lines+markers', line=dict(color=color), marker=dict(size=10))])
            fig.update_layout(title=title, template='plotly_white', margin=dict(l=40, r=40, t=60, b=40))
            # Save to a temporary HTML file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmpfile:
                pio.write_html(fig, file=tmpfile.name, full_html=True)
                webbrowser.open('file://' + os.path.abspath(tmpfile.name))
        except Exception as e:
            print(f"Error opening Plotly in browser: {e}")
        # If a custom click callback is set, call it as well
        if self.click_callback:
            self.click_callback()
            
    def sizeHint(self):
        return QSize(400, 300) 
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objs as go
import plotly.io as pio

class PlotlyDialog(QDialog):
    def __init__(self, title, data, labels=None, chart_type='line', color='#3498db', parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(900, 600)
        layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        # Generate Plotly figure
        fig = self._create_figure(title, data, labels, chart_type, color)
        html = pio.to_html(fig, full_html=False)
        self.web_view.setHtml(html)

    def _create_figure(self, title, data, labels, chart_type, color):
        if chart_type == 'bar':
            fig = go.Figure([go.Bar(x=labels, y=data, marker_color=color)])
        else:
            fig = go.Figure([go.Scatter(x=labels, y=data, mode='lines+markers', line=dict(color=color), marker=dict(size=10))])
        fig.update_layout(title=title, template='plotly_white', margin=dict(l=40, r=40, t=60, b=40))
        return fig 
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
import firebase_admin
from firebase_admin import credentials, firestore
from transformers import pipeline
import torch
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt5.QtGui import QIcon, QFont, QColor

# --- Begin full class implementations ---

class AIAnalyzer:
    """Reusable AI analyzer using Hugging Face models"""
    _instance = None
    _models = {}
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_models()
        return cls._instance
    def _initialize_models(self):
        self.device = 0 if torch.cuda.is_available() else -1
        try:
            self._models['sentiment'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=self.device
            )
            print("AI models loaded successfully")
        except Exception as e:
            print(f"AI model loading error: {e}")
    def analyze_data(self, data: Any, analysis_type: str = "general") -> str:
        try:
            if analysis_type == "sentiment" and isinstance(data, str):
                return self._analyze_sentiment(data)
            elif analysis_type == "sales" and isinstance(data, (list, dict)):
                return self._analyze_sales(data)
            elif analysis_type == "inventory" and isinstance(data, dict):
                return self._analyze_inventory(data)
            elif analysis_type == "trend" and isinstance(data, list):
                return self._analyze_trend(data)
            else:
                return self._general_analysis(data)
        except Exception as e:
            return f"Analysis error: {str(e)}"
    def _analyze_sentiment(self, text: str) -> str:
        if 'sentiment' not in self._models:
            return "Sentiment analysis unavailable"
        result = self._models['sentiment'](text)
        sentiment = result[0]['label']
        confidence = result[0]['score']
        return f"{sentiment} sentiment ({confidence:.1%} confidence)"
    def _analyze_sales(self, data: Any) -> str:
        if isinstance(data, dict):
            amount = data.get('total', data.get('amount', 0))
            count = data.get('count', 1)
            return f"Avg: ${amount/count:.2f} per transaction"
        elif isinstance(data, list) and data:
            total = sum(float(item.get('amount', 0)) for item in data if isinstance(item, dict))
            return f"Total: ${total:.2f} from {len(data)} transactions"
        return "No sales data to analyze"
    def _analyze_inventory(self, data: Dict) -> str:
        total = data.get('total', 0)
        low_stock = data.get('low_stock', 0)
        if low_stock > 0:
            return f"⚠️ {low_stock} items need restocking"
        elif total < 50:
            return "📦 Inventory running low"
        return "✅ Inventory levels healthy"
    def _analyze_trend(self, data: List) -> str:
        if len(data) < 2:
            return "Insufficient data for trend analysis"
        recent = data[-3:] if len(data) >= 3 else data[-2:]
        older = data[:-3] if len(data) >= 3 else data[:-2]
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older) if older else recent_avg
        if recent_avg > older_avg * 1.1:
            return "📈 Trending upward"
        elif recent_avg < older_avg * 0.9:
            return "📉 Trending downward"
        return "➡️ Stable trend"
    def _general_analysis(self, data: Any) -> str:
        current_time = datetime.now().strftime("%H:%M")
        if isinstance(data, (int, float)):
            if data > 1000:
                return f"🚀 High value: {data} (Updated: {current_time})"
            elif data == 0:
                return f"⚡ Start of something new (Updated: {current_time})"
        return f"📊 Data updated at {current_time}"

class FirebaseConnector:
    """Reusable Firebase connector"""
    _instance = None
    def __new__(cls, config: Dict[str, Any] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_firebase(config)
        return cls._instance
    def _initialize_firebase(self, config: Dict[str, Any] = None):
        self.db = None
        self.listeners = {}
        try:
            if not firebase_admin._apps:
                if config and config.get('credentials_path'):
                    cred = credentials.Certificate(config['credentials_path'])
                    firebase_admin.initialize_app(cred)
                else:
                    firebase_admin.initialize_app()
            self.db = firestore.client()
            print("Firebase connected successfully")
        except Exception as e:
            print(f"Firebase connection error: {e}")
    def fetch_data(self, collection: str, filters: Dict[str, Any] = None, limit: int = None) -> List[Dict]:
        if not self.db:
            return []
        try:
            query = self.db.collection(collection)
            if filters:
                for field, value in filters.items():
                    if isinstance(value, dict):
                        for operator, filter_value in value.items():
                            query = query.where(field, operator, filter_value)
                    else:
                        query = query.where(field, '==', value)
            if limit:
                query = query.limit(limit)
            docs = query.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Data fetch error: {e}")
            return []
    def listen_to_changes(self, collection: str, callback: Callable, filters: Dict[str, Any] = None):
        if not self.db:
            return None
        try:
            query = self.db.collection(collection)
            if filters:
                for field, value in filters.items():
                    query = query.where(field, '==', value)
            def on_snapshot(docs, changes, read_time):
                for change in changes:
                    if change.type.name in ['ADDED', 'MODIFIED']:
                        doc_data = {'id': change.document.id, **change.document.to_dict()}
                        callback(doc_data, change.type.name)
            listener = query.on_snapshot(on_snapshot)
            self.listeners[collection] = listener
            return listener
        except Exception as e:
            print(f"Listener setup error: {e}")
            return None
    def stop_listeners(self):
        for listener in self.listeners.values():
            listener.unsubscribe()
        self.listeners.clear()

class DataProcessor(QThread):
    """Reusable data processing thread"""
    data_ready = pyqtSignal(dict)
    analysis_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.firebase = FirebaseConnector(config.get('firebase'))
        self.ai = AIAnalyzer()
        self.running = True
    def run(self):
        try:
            data = self.firebase.fetch_data(
                collection=self.config['collection'],
                filters=self.config.get('filters'),
                limit=self.config.get('limit')
            )
            processed_data = self._process_data(data)
            analysis_result = self.ai.analyze_data(
                processed_data, 
                self.config.get('analysis_type', 'general')
            )
            self.data_ready.emit(processed_data)
            self.analysis_ready.emit(analysis_result)
        except Exception as e:
            self.error_occurred.emit(str(e))
    def _process_data(self, raw_data: List[Dict]) -> Dict[str, Any]:
        processor_type = self.config.get('processor_type', 'count')
        if processor_type == 'count':
            return {'value': len(raw_data), 'items': raw_data}
        elif processor_type == 'sum':
            field = self.config.get('sum_field', 'amount')
            total = sum(float(item.get(field, 0)) for item in raw_data)
            return {'value': total, 'count': len(raw_data), 'items': raw_data}
        elif processor_type == 'average':
            field = self.config.get('avg_field', 'rating')
            values = [float(item.get(field, 0)) for item in raw_data if item.get(field)]
            avg = sum(values) / len(values) if values else 0
            return {'value': round(avg, 2), 'count': len(values), 'items': raw_data}
        elif processor_type == 'status_count':
            status_field = self.config.get('status_field', 'status')
            target_status = self.config.get('target_status', 'active')
            matching = [item for item in raw_data if item.get(status_field) == target_status]
            return {'value': len(matching), 'total': len(raw_data), 'items': matching}
        elif processor_type == 'trend':
            field = self.config.get('trend_field', 'amount')
            values = [float(item.get(field, 0)) for item in raw_data]
            return {'value': values[-1] if values else 0, 'trend_data': values, 'items': raw_data}
        else:
            return {'value': len(raw_data), 'items': raw_data}

class ReusableShopInfoCard(QFrame):
    """Reusable InfoCard template for any shop data type"""
    clicked = pyqtSignal()
    data_updated = pyqtSignal(dict)
    alert_triggered = pyqtSignal(str, str)
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = self._parse_config(config) if isinstance(config, dict) else {'title': str(config), 'color': '#3498db', 'icon': '📊'}
        self.title = self.config['title']
        self.color = self.config['color']
        self.icon = self.config.get('icon', '📊')
        self.current_value = "Loading..."
        self.current_subtitle = ""
        self.last_update = None
        self.notifications = []
        self.max_notifications = 5
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._refresh_data)
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self._update_display)
        self.notification_timer.start(3000)
        self._setup_ui()
        if self.config.get('auto_update', True):
            self.start_updates()
    def _parse_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        default_config = {
            'title': 'Shop Metric',
            'color': '#3498db',
            'icon': '📊',
            'collection': 'default',
            'processor_type': 'count',
            'analysis_type': 'general',
            'update_interval': 30000,
            'auto_update': True,
            'firebase': {},
            'alerts': {
                'enabled': False,
                'thresholds': {}
            },
            'format': {
                'value_prefix': '',
                'value_suffix': '',
                'decimal_places': 0
            }
        }
        merged_config = {**default_config, **config}
        if not merged_config.get('collection'):
            raise ValueError("Collection name is required")
        return merged_config
    def _setup_ui(self):
        self.setObjectName("reusableShopCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumSize(280, 180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(self._get_stylesheet())
        self.setCursor(Qt.PointingHandCursor)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 20, 25, 20)
        self.layout.setSpacing(12)
        header_layout = QHBoxLayout()
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        header_layout.addWidget(icon_label)
        title_label = QLabel(self.title)
        title_label.setObjectName("cardTitle")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.status_indicator = QLabel("●")
        self.status_indicator.setObjectName("statusDot")
        self.status_indicator.setFont(QFont("Arial", 12))
        header_layout.addWidget(self.status_indicator)
        self.layout.addLayout(header_layout)
        self.value_label = QLabel(str(self.current_value))
        self.value_label.setObjectName("cardValue")
        self.value_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {self.color};")
        self.layout.addWidget(self.value_label)
        self.subtitle_label = QLabel(self.current_subtitle)
        self.subtitle_label.setObjectName("cardSubtitle")
        self.subtitle_label.setFont(QFont("Segoe UI", 13))
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setMinimumHeight(40)
        self.layout.addWidget(self.subtitle_label)
        self.update_label = QLabel("Never updated")
        self.update_label.setObjectName("updateLabel")
        self.update_label.setFont(QFont("Segoe UI", 10))
        self.update_label.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.update_label)
        self.layout.addStretch()
    def start_updates(self):
        self._refresh_data()
        self.update_timer.start(self.config['update_interval'])
        self._set_status("connected")
    def stop_updates(self):
        self.update_timer.stop()
        self._set_status("disconnected")
    @pyqtSlot()
    def _refresh_data(self):
        self._set_status("updating")
        self.data_processor = DataProcessor(self.config)
        self.data_processor.data_ready.connect(self._handle_data_update)
        self.data_processor.analysis_ready.connect(self._handle_analysis_update)
        self.data_processor.error_occurred.connect(self._handle_error)
        self.data_processor.start()
    @pyqtSlot(dict)
    def _handle_data_update(self, data: Dict[str, Any]):
        try:
            value = data.get('value', 0)
            formatted_value = self._format_value(value)
            self.current_value = formatted_value
            self.value_label.setText(str(formatted_value))
            self.last_update = datetime.now()
            if self.config['alerts']['enabled']:
                self._check_alerts(value)
            self.data_updated.emit(data)
            self._set_status("connected")
        except Exception as e:
            self._handle_error(f"Data update error: {str(e)}")
    @pyqtSlot(str)
    def _handle_analysis_update(self, analysis: str):
        self._add_notification(analysis, "ai")
    @pyqtSlot(str)
    def _handle_error(self, error_message: str):
        self._add_notification(f"Error: {error_message}", "error")
        self._set_status("error")
    def _format_value(self, value: Any) -> str:
        format_config = self.config['format']
        if isinstance(value, (int, float)):
            decimal_places = format_config.get('decimal_places', 0)
            if decimal_places > 0:
                formatted = f"{value:.{decimal_places}f}"
            else:
                formatted = f"{int(value)}"
        else:
            formatted = str(value)
        prefix = format_config.get('value_prefix', '')
        suffix = format_config.get('value_suffix', '')
        return f"{prefix}{formatted}{suffix}"
    def _check_alerts(self, value: float):
        thresholds = self.config['alerts']['thresholds']
        for threshold_name, threshold_config in thresholds.items():
            condition = threshold_config.get('condition', 'greater_than')
            threshold_value = threshold_config.get('value', 0)
            message = threshold_config.get('message', f"Alert: {threshold_name}")
            level = threshold_config.get('level', 'warning')
            triggered = False
            if condition == 'greater_than' and value > threshold_value:
                triggered = True
            elif condition == 'less_than' and value < threshold_value:
                triggered = True
            elif condition == 'equals' and value == threshold_value:
                triggered = True
            if triggered:
                self._add_notification(message, level)
                self.alert_triggered.emit(message, level)
    def _add_notification(self, message: str, level: str = "info"):
        notification = {
            'message': message,
            'level': level,
            'timestamp': datetime.now()
        }
        self.notifications.insert(0, notification)
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[:self.max_notifications]
    @pyqtSlot()
    def _update_display(self):
        cutoff_time = datetime.now() - timedelta(minutes=5)
        self.notifications = [n for n in self.notifications if n['timestamp'] > cutoff_time]
        if self.notifications:
            latest = self.notifications[0]
            subtitle_text = f"{latest['message']} ({latest['timestamp'].strftime('%H:%M')})"
        else:
            subtitle_text = ""
        self.subtitle_label.setText(subtitle_text)
        if self.last_update:
            time_ago = datetime.now() - self.last_update
            if time_ago.seconds < 60:
                update_text = "Just updated"
            elif time_ago.seconds < 3600:
                update_text = f"Updated {time_ago.seconds // 60}m ago"
            else:
                update_text = f"Updated {time_ago.seconds // 3600}h ago"
            self.update_label.setText(update_text)
    def _set_status(self, status: str):
        status_colors = {
            "connected": "#2ecc71",
            "updating": "#f39c12",
            "error": "#e74c3c",
            "disconnected": "#95a5a6"
        }
        color = status_colors.get(status, "#95a5a6")
        self.status_indicator.setStyleSheet(f"color: {color};")
    def _get_stylesheet(self):
        return f"""
        QFrame#reusableShopCard {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border-radius: 16px;
            border: 2px solid #e9ecef;
        }}
        QFrame#reusableShopCard:hover {{
            border: 2px solid {self.color};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f1f3f4);
        }}
        QLabel#cardTitle {{
            color: #2c3e50;
            background: transparent;
        }}
        QLabel#cardValue {{
            background: transparent;
            padding: 5px 0px;
        }}
        QLabel#cardSubtitle {{
            color: #6c757d;
            background: transparent;
            padding: 2px 4px;
            border-radius: 4px;
        }}
        QLabel#updateLabel {{
            color: #adb5bd;
            background: transparent;
        }}
        QLabel#statusDot {{
            background: transparent;
        }}
        """
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    def update_config(self, new_config: Dict[str, Any]):
        self.config.update(new_config)
        if 'title' in new_config:
            self.title = new_config['title']
        if 'color' in new_config:
            self.color = new_config['color']
            self.setStyleSheet(self._get_stylesheet())
    def manual_refresh(self):
        self._refresh_data()
    def add_custom_notification(self, message: str, level: str = "info"):
        self._add_notification(message, level)
    def update_values(self, value=None, subtitle=None, color=None):
        """
        Update the value, subtitle, and optionally the color of the card.
        """
        if value is not None:
            self.value_label.setText(str(value))
        if subtitle is not None:
            self.subtitle_label.setText(str(subtitle))
        if color is not None:
            self.value_label.setStyleSheet(f"color: {color};")

class ShopCardPresets:
    @staticmethod
    def daily_sales(firebase_config: Dict[str, Any]) -> Dict[str, Any]:
        today = datetime.now().date()
        return {
            'title': 'Daily Sales',
            'color': '#27ae60',
            'icon': '💰',
            'collection': 'sales',
            'processor_type': 'sum',
            'sum_field': 'amount',
            'analysis_type': 'sales',
            'filters': {
                'date': {'>=': today}
            },
            'format': {
                'value_prefix': '$',
                'decimal_places': 2
            },
            'alerts': {
                'enabled': True,
                'thresholds': {
                    'low_sales': {
                        'condition': 'less_than',
                        'value': 100,
                        'message': '⚠️ Daily sales below target',
                        'level': 'warning'
                    },
                    'high_sales': {
                        'condition': 'greater_than',
                        'value': 1000,
                        'message': '🎉 Excellent sales day!',
                        'level': 'success'
                    }
                }
            },
            'firebase': firebase_config
        }
    @staticmethod
    def inventory_count(firebase_config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'title': 'Total Inventory',
            'color': '#3498db',
            'icon': '📦',
            'collection': 'inventory',
            'processor_type': 'sum',
            'sum_field': 'quantity',
            'analysis_type': 'inventory',
            'format': {
                'value_suffix': ' items'
            },
            'alerts': {
                'enabled': True,
                'thresholds': {
                    'low_inventory': {
                        'condition': 'less_than',
                        'value': 50,
                        'message': '📦 Low inventory alert',
                        'level': 'warning'
                    }
                }
            },
            'firebase': firebase_config
        }
    @staticmethod
    def active_customers(firebase_config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'title': 'Active Customers',
            'color': '#9b59b6',
            'icon': '👥',
            'collection': 'customers',
            'processor_type': 'status_count',
            'status_field': 'status',
            'target_status': 'active',
            'analysis_type': 'general',
            'firebase': firebase_config
        }
    @staticmethod
    def average_rating(firebase_config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'title': 'Avg Rating',
            'color': '#f39c12',
            'icon': '⭐',
            'collection': 'reviews',
            'processor_type': 'average',
            'avg_field': 'rating',
            'analysis_type': 'sentiment',
            'format': {
                'decimal_places': 1,
                'value_suffix': '/5'
            },
            'firebase': firebase_config
        }
    @staticmethod
    def pending_orders(firebase_config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'title': 'Pending Orders',
            'color': '#e74c3c',
            'icon': '📋',
            'collection': 'orders',
            'processor_type': 'status_count',
            'status_field': 'status',
            'target_status': 'pending',
            'analysis_type': 'general',
            'alerts': {
                'enabled': True,
                'thresholds': {
                    'many_pending': {
                        'condition': 'greater_than',
                        'value': 10,
                        'message': '⚠️ Many pending orders need attention',
                        'level': 'warning'
                    }
                }
            },
            'firebase': firebase_config
        }

# --- End full class implementations --- 
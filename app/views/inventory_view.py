from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLineEdit, QSizePolicy, QSpacerItem, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont

class InventoryView(QWidget):
    def __init__(self, controller=None, user_role="Admin"):
        super().__init__()
        self.controller = controller
        self.user_role = user_role

        # Placeholder values
        self.stock_count = 0
        self.low_stock_items = 0
        self.recent_items = 0

        # Card labels for dynamic updates
        self.card_labels = {}

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Smart Shop Manager - Inventory")
        self.setGeometry(100, 100, 1300, 900)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 10px;
                background-color: #ffffff;
            }
        """)

        self.last_updated_time = QDateTime.currentDateTime()
        main_layout = QVBoxLayout()

        # Alert Bar
        alerts_label = QLabel("ℹ️ Low Stock: 3 Items  |  ⚠️ Pending Orders: 2  |  🛡️ Security Alert: 1")
        alerts_label.setStyleSheet("background-color: #eef6ff; font-weight: 600; padding: 8px;")
        main_layout.addWidget(alerts_label)

        # Header
        main_layout.addLayout(self.build_header())

        # Cards Area
        self.card_area = self.build_grid_cards()
        main_layout.addLayout(self.card_area)

        # Footer
        self.footer_label = QLabel()
        self.footer_label.setStyleSheet("background-color: #F7F7F7; padding: 6px; font-style: italic;")
        self.update_footer_time()
        main_layout.addWidget(self.footer_label)

        timer = QTimer(self)
        timer.timeout.connect(self.update_footer_time)
        timer.start(60000)

        self.setLayout(main_layout)

        self.refresh_from_controller()

    def build_header(self):
        header = QHBoxLayout()
        header.setSpacing(12)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search...")
        self.search_bar.setFixedWidth(320)
        self.search_bar.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #ccc;")

        date_filter = QLineEdit()
        date_filter.setPlaceholderText("📅 Date Filter")
        date_filter.setFixedWidth(200)
        date_filter.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #ccc;")

        header.addWidget(self.search_bar)
        header.addWidget(date_filter)
        header.addStretch()

        for text, color in [("🔔 Notification", "#3498db"), ("👤 Admin", "#2ecc71"), ("🔴 Turn off", "#e74c3c")]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: #333;
                }}
            """)
            header.addWidget(btn)

        return header

    def build_grid_cards(self):
        grid = QGridLayout()
        grid.setSpacing(20)

        self.card_labels = {
            "stock": self.create_card("📦 Total Stock", "0\nUpdated: just now"),
            "low": self.create_card("⚠️ Low Stock Items", "0\nRestock Suggested"),
            "recent": self.create_card("🆕 Recently Added", "0\nLast Added: few minutes ago"),
            "sales": self.create_card("📊 Category-wise Sales", "Graph\n..."),
            "report": self.create_card("📄 Recommendation & Report", "FOR New stock up and recent stock"),
            "upload": self.create_card("📥 Bulk Stock Upload", "Import CSV/XLS here"),
        }

        grid.addWidget(self.card_labels["stock"]["widget"], 0, 0)
        grid.addWidget(self.card_labels["low"]["widget"], 0, 1)
        grid.addWidget(self.card_labels["recent"]["widget"], 0, 2)
        grid.addWidget(self.card_labels["sales"]["widget"], 1, 0)
        grid.addWidget(self.card_labels["report"]["widget"], 1, 1)
        grid.addWidget(self.card_labels["upload"]["widget"], 1, 2)

        return grid

    def create_card(self, title, content):
        box = QGroupBox(title)
        layout = QVBoxLayout()
        label = QLabel(content)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 13px; color: #555;")
        layout.addWidget(label)
        layout.addStretch()
        box.setLayout(layout)
        box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return {"widget": box, "label": label}

    def update_footer_time(self):
        self.footer_label.setText(f"Last synced: {QDateTime.currentDateTime().toString('hh:mm ap - dd MMM yyyy')}")

    def update_stock_info(self, stock, low_stock, recent):
        self.card_labels["stock"]["label"].setText(f"{stock:,}\nUpdated: just now")
        self.card_labels["low"]["label"].setText(f"{low_stock}\nRestock Suggested")
        self.card_labels["recent"]["label"].setText(f"{recent}\nLast Added: few minutes ago")

    def refresh_from_controller(self):
        if self.controller:
            stock = self.controller.count_total_stock()
            low = self.controller.count_low_stock()
            recent = self.controller.count_recent_items()
            self.update_stock_info(stock, low, recent)

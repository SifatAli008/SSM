# inventory_view.py (Refactored & Enhanced)
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLineEdit, QSizePolicy, QSpacerItem, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont


class InventoryView(QWidget):
    def __init__(self, user_role="Admin"):
        super().__init__()
        self.user_role = user_role
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Smart Shop Manager - Inventory")
        self.setGeometry(100, 100, 1300, 900)
        self.setStyleSheet("font-family: Segoe UI; font-size: 14px;")

        self.last_updated_time = QDateTime.currentDateTime()

        # ---------- Main Layout ----------
        main_layout = QVBoxLayout()

        # Top Status Bar
        alerts_label = QLabel("ℹ️ Low Stock: 3 Items  |  ⚠️ Pending Orders: 2  |  🛡️ Security Alert: 1")
        alerts_label.setStyleSheet("background-color: #eaf4ff; font-weight: bold; padding: 6px;")
        main_layout.addWidget(alerts_label)

        # ---------- Header ----------
        main_layout.addLayout(self.build_header())

        # ---------- Cards Layout ----------
        self.stock_count = 5000
        self.low_stock_items = 7
        self.recent_items = 12
        main_layout.addLayout(self.build_grid_cards())

        # ---------- Footer ----------
        self.footer_label = QLabel()
        self.footer_label.setStyleSheet("background-color: #F0F0F0; padding: 6px; font-style: italic;")
        self.update_footer_time()
        main_layout.addWidget(self.footer_label)

        # Auto update timer every minute
        timer = QTimer(self)
        timer.timeout.connect(self.update_footer_time)
        timer.start(60000)

        self.setLayout(main_layout)

    # ---------- Header Section ----------
    def build_header(self):
        header = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search...")
        self.search_bar.setFixedWidth(300)

        date_filter = QLineEdit()
        date_filter.setPlaceholderText("📅 Date Filter")
        date_filter.setFixedWidth(200)

        header.addWidget(self.search_bar)
        header.addWidget(date_filter)
        header.addStretch()

        for text in ["🔔 Notification", "👤 Admin", "🔴 Turn off"]:
            btn = QPushButton(text)
            btn.setStyleSheet("padding: 6px 14px;")
            header.addWidget(btn)

        return header

    # ---------- Cards Layout ----------
    def build_grid_cards(self):
        grid = QGridLayout()

        grid.addWidget(self.create_card("📦 Total Stock", f"{self.stock_count}\nUpdated: just now"), 0, 0)
        grid.addWidget(self.create_card("⚠️ Low Stock Items", f"{self.low_stock_items}\nRestock Suggested"), 0, 1)
        grid.addWidget(self.create_card("🆕 Recently Added", f"{self.recent_items}\nLast Added: 10 min ago"), 0, 2)

        grid.addWidget(self.create_card("📊 Category-wise Sales", "Graph\n..."), 1, 0)
        grid.addWidget(self.create_card("📄 Recommendation & Report", "FOR New stock up and recent stock"), 1, 1)
        grid.addWidget(self.create_card("📥 Bulk Stock Upload", "Import CSV/XLS here"), 1, 2)

        return grid

    # ---------- Card Component ----------
    def create_card(self, title, content):
        box = QGroupBox(title)
        layout = QVBoxLayout()
        label = QLabel(content)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 13px;")
        layout.addWidget(label)
        box.setLayout(layout)
        box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return box

    # ---------- Footer Update ----------
    def update_footer_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm AP")
        self.footer_label.setText(
            f"🕔 Last System Closed: 08:00 PM | System Opened: 10:00 AM | 👤 User: 1 | 🕒 Time: {current_time}"
        )

    # ---------- Dynamic Update Methods (Future Hookups) ----------
    def update_stock_info(self, stock, low_stock, recent):
        self.stock_count = stock
        self.low_stock_items = low_stock
        self.recent_items = recent
        self.init_ui()

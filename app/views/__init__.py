# File: E:\UDH\smart_shop_manager\app\views\__init__.py

# This file makes the 'views' directory a Python package.
# You typically don't need to put much here unless you want to expose certain imports.

# Optionally, expose common views here if you want easier imports elsewhere in the project.

from .dashboard_view import DashboardPage
from .inventory_view import InventoryView
from .main_window import MainWindow

__all__ = [
    "DashboardPage",
    "InventoryView",
    "MainWindow",
]

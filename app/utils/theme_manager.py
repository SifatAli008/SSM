"""
Smart Shop Manager - Theme Manager
This module provides centralized theme management for the application.
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QFont
from enum import Enum

class ThemeType(Enum):
    """Enum for available themes"""
    LIGHT = "light"
    # Removed other themes to keep only Light theme

class ThemeManager:
    """Centralized theme management for consistent UI appearance"""
    
    # Default theme colors (light theme)
    COLORS = {
        "primary": "#3B82F6",         # Blue (accent color)
        "primary_light": "#60A5FA",   # Lighter blue
        "primary_dark": "#2563EB",    # Darker blue (hover/pressed)
        "accent": "#8B5CF6",          # Purple variant
        "success": "#10B981",         # Green
        "warning": "#F59E0B",         # Yellow
        "danger": "#EF4444",          # Red
        "info": "#0EA5E9",            # Info blue
        "background": "#F9FAFB",      # Soft white (primary background)
        "card": "#FFFFFF",            # White
        "text_primary": "#111827",    # Charcoal/Dark Gray
        "text_secondary": "#6B7280",  # Medium Gray
        "border": "#D1D5DB",          # Light Border Gray
        "hover": "#F3F4F6",           # Very light gray for hover states
        "sidebar": "#E5E7EB",         # Light Gray (secondary background)
        "sidebar_text": "#111827"     # Charcoal (primary text color)
    }
    
    # Font settings
    FONTS = {
        "family": "Segoe UI",
        "size_small": 11,       # Slightly increased for better readability
        "size_normal": 13,      # Increased from 12
        "size_large": 15,       # Increased from 14
        "size_xlarge": 20,      # Increased from 18
        "size_xxlarge": 26      # Increased from 24
    }
    
    # Border radius
    BORDER_RADIUS = {
        "small": 6,             # Increased from 4
        "normal": 8,
        "large": 12
    }
    
    # Spacing
    SPACING = {
        "small": 6,             # Increased from 5
        "normal": 12,           # Increased from 10
        "large": 18,            # Increased from 15
        "xlarge": 24            # Increased from 20
    }
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._current_theme = ThemeType.LIGHT
        return cls._instance
    
    @classmethod
    def get_color(cls, color_name):
        """Get a color by name from the current theme"""
        if color_name in cls.COLORS:
            return cls.COLORS[color_name]
        return "#000000"  # Default to black if color not found
    
    @classmethod
    def set_theme(cls, theme_type):
        """Set the current theme"""
        instance = cls()
        instance._current_theme = ThemeType.LIGHT  # Always set to Light theme
        
        # Apply light theme regardless of the input
        cls._apply_light_theme()
    
    @classmethod
    def _apply_light_theme(cls):
        """Apply light theme colors"""
        # Just apply the app stylesheet since colors are already set
        cls._apply_app_stylesheet()
    
    @classmethod
    def _apply_app_stylesheet(cls):
        """Apply the stylesheet to the application"""
        app = QApplication.instance()
        if app:
            app.setStyleSheet(cls.get_app_stylesheet())
    
    @classmethod
    def get_app_stylesheet(cls):
        """Get the application stylesheet as a string"""
        c = cls.COLORS
        return f"""
            /* Global application style */
            QWidget {{
                font-family: "{cls.FONTS['family']}";
                font-size: {cls.FONTS['size_normal']}px;
                color: {c["text_primary"]};
                background-color: {c["background"]};
            }}
            
            /* Main window */
            QMainWindow {{
                background-color: {c["background"]};
            }}
            
            /* All labels should have transparent backgrounds by default */
            QLabel {{
                color: {c["text_primary"]};
                background-color: transparent;
            }}
            
            /* Title headers - consistent sizing */
            QLabel[objectName="page-title"],
            QLabel[objectName="title"],
            QLabel.title {{
                font-size: {cls.FONTS['size_xxlarge']}px;
                font-weight: bold;
                color: {c["text_primary"]};
                background-color: transparent;
            }}
            
            /* Subtitle headers - consistent sizing */
            QLabel[objectName="page-subtitle"],
            QLabel[objectName="subtitle"],
            QLabel.subtitle {{
                font-size: {cls.FONTS['size_large']}px;
                color: {c["text_secondary"]};
                background-color: transparent;
            }}
            
            /* Sidebar style */
            QWidget#sidebar {{
                background-color: {c["sidebar"]};
                color: {c["sidebar_text"]};
                border-right: 1px solid {c["border"]};
            }}
            
            /* Navigation buttons */
            QWidget#nav-container QPushButton {{
                color: {c["sidebar_text"]};
                border: none;
                text-align: left;
                padding: 12px 16px;
                font-size: 15px;
                border-radius: {cls.BORDER_RADIUS['normal']}px;
                margin: 4px 8px;
                background-color: transparent;
            }}
            
            QWidget#nav-container QPushButton:hover {{
                background-color: {c["hover"]};
            }}
            
            QWidget#nav-container QPushButton:checked {{
                background-color: {c["primary"]};
                color: white;
                font-weight: bold;
            }}
            
            /* Content area */
            QWidget#content-stack {{
                background-color: {c["background"]};
            }}
            
            /* Cards and frames */
            QFrame.card {{
                background-color: {c["card"]};
                border-radius: {cls.BORDER_RADIUS['normal']}px;
                border: 1px solid {c["border"]};
            }}
            
            /* Ensure all widgets inside cards have transparent backgrounds */
            QFrame.card QWidget {{
                background-color: transparent;
            }}
            
            QFrame.card QLabel {{
                background-color: transparent;
            }}
            
            /* Push buttons */
            QPushButton {{
                background-color: {c["primary"]};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: {cls.BORDER_RADIUS['small']}px;
                font-weight: bold;
                font-size: {cls.FONTS['size_normal']}px;
                min-height: 36px;
                min-width: 90px;
            }}
            
            QPushButton:hover {{
                background-color: {c["primary_dark"]};
            }}
            
            QPushButton:pressed {{
                background-color: {c["primary_light"]};
                padding-top: 9px;
                padding-left: 17px;
            }}
            
            QPushButton:disabled {{
                background-color: #D1D5DB;
                color: #6B7280;
            }}
            
            /* Secondary buttons */
            QPushButton.secondary {{
                background-color: {c["accent"]};
                color: white;
            }}
            
            QPushButton.secondary:hover {{
                background-color: #7C3AED;
            }}
            
            QPushButton.success {{
                background-color: {c["success"]};
                color: white;
            }}
            
            QPushButton.success:hover {{
                background-color: #059669;
            }}
            
            QPushButton.warning {{
                background-color: {c["warning"]};
                color: white;
            }}
            
            QPushButton.warning:hover {{
                background-color: #D97706;
            }}
            
            QPushButton.danger {{
                background-color: {c["danger"]};
                color: white;
            }}
            
            QPushButton.danger:hover {{
                background-color: #DC2626;
            }}
            
            /* Ensure all flat buttons have transparent backgrounds */
            QPushButton[flat="true"] {{
                background-color: transparent;
                min-height: 30px;
                min-width: 0px;
            }}
            
            /* Line edits and text inputs */
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                padding: 12px;
                border: 1px solid {c["border"]};
                border-radius: {cls.BORDER_RADIUS['small']}px;
                background-color: {c["card"]};
                color: {c["text_primary"]};
                font-size: {cls.FONTS['size_normal']}px;
                min-height: 24px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 2px solid {c["primary"]};
                outline: none;
            }}
            
            /* Combobox */
            QComboBox {{
                padding-right: 20px;
                color: {c["text_primary"]};
                background-color: {c["card"]};
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border-left: 1px solid {c["border"]};
                width: 20px;
            }}
            
            QComboBox::drop-down:on {{
                background-color: {c["primary"]};
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {c["card"]};
                border: 1px solid {c["border"]};
                selection-background-color: {c["primary"]};
                selection-color: white;
                color: {c["text_primary"]};
                outline: none;
            }}
            
            QComboBox QAbstractItemView::item {{
                background-color: {c["card"]};
                color: {c["text_primary"]};
                padding: 6px;
                min-height: 24px;
            }}
            
            QComboBox QAbstractItemView::item:selected {{
                background-color: {c["primary"]};
                color: white;
            }}
            
            QComboBox QAbstractItemView::item:hover:!selected {{
                background-color: {c["hover"]};
            }}
            
            /* Checkboxes */
            QCheckBox {{
                spacing: 8px;
                background-color: transparent;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {c["border"]};
                border-radius: 4px;
                background-color: {c["card"]};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {c["primary"]};
            }}
            
            QCheckBox::indicator:hover {{
                border: 1px solid {c["primary"]};
            }}
            
            /* Tab Widget */
            QTabWidget::pane {{
                border: 1px solid {c["border"]};
                border-radius: {cls.BORDER_RADIUS['small']}px;
                background-color: {c["card"]};
                top: -1px;
            }}
            
            QTabBar::tab {{
                background-color: {c["background"]};
                border: 1px solid {c["border"]};
                padding: 8px 16px;
                border-top-left-radius: {cls.BORDER_RADIUS['small']}px;
                border-top-right-radius: {cls.BORDER_RADIUS['small']}px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {c["primary"]};
                color: white;
                border-bottom-color: {c["card"]};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {c["hover"]};
            }}
            
            /* Table widget */
            QTableWidget {{
                gridline-color: {c["border"]};
                background-color: {c["card"]};
                border: 1px solid {c["border"]};
                border-radius: {cls.BORDER_RADIUS['small']}px;
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {c["border"]};
            }}
            
            QTableWidget::item:selected {{
                background-color: {c["primary"]};
                color: white;
            }}
            
            /* Fix for cell editing - important to override any default styles */
            QTableWidget QLineEdit, QTableView QLineEdit {{
                background-color: white;
                color: black;
                border: 2px solid {c["primary"]};
                padding: 2px 5px;
                margin: 0px;
                selection-background-color: {c["primary"]};
                selection-color: white;
                font-family: "{cls.FONTS['family']}";
                font-size: {cls.FONTS['size_normal']}px;
            }}
            
            QHeaderView::section {{
                background-color: {c["background"]};
                padding: 8px;
                border: 1px solid {c["border"]};
                font-weight: bold;
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                border: none;
                background: {c["background"]};
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {c["border"]};
                min-height: 30px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {c["text_secondary"]};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: {c["background"]};
                height: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {c["border"]};
                min-width: 30px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background: {c["text_secondary"]};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* Message boxes */
            QMessageBox {{
                background-color: {c["card"]};
            }}
            
            QMessageBox QLabel {{
                color: {c["text_primary"]};
                background-color: transparent;
            }}
            
            QMessageBox QPushButton {{
                min-width: 80px;
                min-height: 30px;
            }}
            
            /* Dialog style */
            QDialog {{
                background-color: {c["background"]};
            }}
            
            /* Group boxes */
            QGroupBox {{
                background-color: transparent;
                border: 1px solid {c["border"]};
                border-radius: {cls.BORDER_RADIUS['small']}px;
                margin-top: 20px;
                font-weight: bold;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {c["text_primary"]};
                background-color: transparent;
            }}
        """
    
    @classmethod
    def apply_palette_to_app(cls):
        """Apply color palette to the application"""
        app = QApplication.instance()
        if not app:
            return
        
        c = cls.COLORS
        palette = QPalette()
        
        # Set window background
        palette.setColor(QPalette.Window, QColor(c["background"]))
        palette.setColor(QPalette.WindowText, QColor(c["text_primary"]))
        
        # Set base colors
        palette.setColor(QPalette.Base, QColor(c["card"]))
        palette.setColor(QPalette.AlternateBase, QColor(c["hover"]))
        
        # Set text colors
        palette.setColor(QPalette.Text, QColor(c["text_primary"]))
        palette.setColor(QPalette.BrightText, QColor(c["text_primary"]))
        palette.setColor(QPalette.ButtonText, QColor("white"))
        
        # Set button, highlight colors
        palette.setColor(QPalette.Button, QColor(c["primary"]))
        palette.setColor(QPalette.Highlight, QColor(c["primary"]))
        palette.setColor(QPalette.HighlightedText, QColor("white"))
        
        # Set disabled colors
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#999999"))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#999999"))
        
        app.setPalette(palette)
    
    @classmethod
    def apply_theme(cls, theme_type=ThemeType.LIGHT):
        """Apply theme to the application (both stylesheet and palette)"""
        cls.set_theme(ThemeType.LIGHT)  # Always use Light theme
        cls.apply_palette_to_app()

# Initialize theme when module is imported
theme_manager = ThemeManager() 
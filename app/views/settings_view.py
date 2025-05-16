"""
Smart Shop Manager - Settings View
File: app/views/settings_view.py

This module provides a settings view for the application including theme selection.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QFrame, QFormLayout,
    QStackedWidget, QListWidget, QListWidgetItem,
    QGroupBox, QCheckBox, QRadioButton, QSpinBox,
    QSlider, QColorDialog, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor

from app.views.widgets.components import PageHeader, Card, Button
from app.views.widgets.layouts import SplitLayout, PageLayout
from app.utils.theme_manager import ThemeManager, ThemeType

class ThemeSelector(QWidget):
    """Theme selection widget"""
    
    theme_changed = pyqtSignal(ThemeType)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Theme options
        themes_group = QGroupBox("Select Theme")
        themes_layout = QVBoxLayout(themes_group)
        
        # Theme radio buttons
        self.theme_radios = {}
        
        themes = [
            ("light", "Light Theme", "Clean, bright interface for daytime use"),
            ("dark", "Dark Theme", "Easy on the eyes for nighttime use"),
            ("blue", "Blue Theme", "Modern blue appearance")
        ]
        
        # Current theme
        current_theme = ThemeManager._instance._current_theme if ThemeManager._instance else ThemeType.LIGHT
        
        for theme_id, theme_name, theme_desc in themes:
            theme_layout = QHBoxLayout()
            
            # Radio button
            radio = QRadioButton(theme_name)
            radio.setChecked(current_theme.value == theme_id)
            
            # Connect signal
            theme_type = getattr(ThemeType, theme_id.upper())
            radio.clicked.connect(lambda checked, t=theme_type: self.on_theme_selected(t))
            
            self.theme_radios[theme_id] = radio
            theme_layout.addWidget(radio)
            
            # Description
            desc_label = QLabel(theme_desc)
            desc_label.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')};")
            theme_layout.addWidget(desc_label)
            theme_layout.addStretch()
            
            themes_layout.addLayout(theme_layout)
        
        layout.addWidget(themes_group)
        
        # Custom theme section
        custom_group = QGroupBox("Custom Theme")
        custom_layout = QVBoxLayout(custom_group)
        
        # Accent color button
        self.accent_btn = QPushButton("Select Accent Color")
        self.accent_btn.clicked.connect(self.select_accent_color)
        custom_layout.addWidget(self.accent_btn)
        
        # Background color button
        self.bg_btn = QPushButton("Select Background Color")
        self.bg_btn.clicked.connect(self.select_bg_color)
        custom_layout.addWidget(self.bg_btn)
        
        # Save theme button
        save_theme_btn = QPushButton("Save Custom Theme")
        save_theme_btn.clicked.connect(self.save_custom_theme)
        custom_layout.addWidget(save_theme_btn)
        
        layout.addWidget(custom_group)
        layout.addStretch()
    
    def on_theme_selected(self, theme_type):
        """Handle theme selection"""
        # Apply theme immediately
        ThemeManager.apply_theme(theme_type)
        
        # Emit signal
        self.theme_changed.emit(theme_type)
    
    def select_accent_color(self):
        """Select accent color for custom theme"""
        current_color = QColor(ThemeManager.get_color("primary"))
        color = QColorDialog.getColor(current_color, self, "Select Accent Color")
        
        if color.isValid():
            # Create custom colors dict
            custom_colors = ThemeManager._instance._custom_colors.copy() if ThemeManager._instance else {}
            custom_colors["primary"] = color.name()
            custom_colors["primary_light"] = QColor(color).lighter(115).name()
            custom_colors["primary_dark"] = QColor(color).darker(115).name()
            
            # Apply custom theme
            ThemeManager._instance._custom_colors = custom_colors
            ThemeManager.apply_theme(ThemeType.CUSTOM)
            
            # Update radio buttons
            for theme_id, radio in self.theme_radios.items():
                radio.setChecked(theme_id == "custom")
            
            # Emit signal
            self.theme_changed.emit(ThemeType.CUSTOM)
    
    def select_bg_color(self):
        """Select background color for custom theme"""
        current_color = QColor(ThemeManager.get_color("background"))
        color = QColorDialog.getColor(current_color, self, "Select Background Color")
        
        if color.isValid():
            # Create custom colors dict
            custom_colors = ThemeManager._instance._custom_colors.copy() if ThemeManager._instance else {}
            custom_colors["background"] = color.name()
            
            # Adjust card color to match
            if color.lightness() < 128:
                # Dark background - lighter cards
                custom_colors["card"] = QColor(color).lighter(150).name()
                custom_colors["text_primary"] = "#ffffff"
                custom_colors["text_secondary"] = "#cccccc"
            else:
                # Light background - white cards
                custom_colors["card"] = "#ffffff"
                custom_colors["text_primary"] = "#2c3e50"
                custom_colors["text_secondary"] = "#7f8c8d"
            
            # Apply custom theme
            ThemeManager._instance._custom_colors = custom_colors
            ThemeManager.apply_theme(ThemeType.CUSTOM)
            
            # Update radio buttons
            for theme_id, radio in self.theme_radios.items():
                radio.setChecked(theme_id == "custom")
            
            # Emit signal
            self.theme_changed.emit(ThemeType.CUSTOM)
    
    def save_custom_theme(self):
        """Save custom theme to file"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Theme", "", "JSON Files (*.json)"
        )
        
        if filepath:
            if not filepath.endswith(".json"):
                filepath += ".json"
            
            success = ThemeManager.save_theme_to_file(filepath)
            
            if success:
                QMessageBox.information(self, "Theme Saved", "Custom theme was saved successfully.")
            else:
                QMessageBox.warning(self, "Save Failed", "Could not save the custom theme.")

class SettingsView(QWidget):
    """Settings view with various application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        # Create page layout
        page_layout = PageLayout()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(page_layout)
        
        # Add page header
        header = PageHeader("Settings", "Configure application preferences")
        page_layout.set_header(header)
        
        # Create split layout for settings
        split = SplitLayout(1, 3)
        
        # Create settings categories list
        categories = QListWidget()
        categories.addItem("Appearance")
        categories.addItem("General")
        categories.addItem("Notifications")
        categories.addItem("Backup & Restore")
        categories.addItem("About")
        
        categories.setCurrentRow(0)
        categories.currentRowChanged.connect(self.on_category_changed)
        
        # Add categories to left panel
        split.add_to_left(categories)
        
        # Create stacked widget for settings pages
        self.settings_stack = QStackedWidget()
        
        # Add appearance settings
        appearance_card = Card("Appearance Settings")
        appearance_layout = QVBoxLayout()
        
        # Theme selector
        theme_selector = ThemeSelector()
        theme_selector.theme_changed.connect(self.on_theme_changed)
        appearance_layout.addWidget(theme_selector)
        
        # Font size slider
        font_group = QGroupBox("Font Size")
        font_layout = QVBoxLayout(font_group)
        
        font_slider = QSlider(Qt.Horizontal)
        font_slider.setMinimum(80)
        font_slider.setMaximum(120)
        font_slider.setValue(100)
        font_layout.addWidget(font_slider)
        
        font_labels = QHBoxLayout()
        font_labels.addWidget(QLabel("Smaller"))
        font_labels.addStretch()
        font_labels.addWidget(QLabel("Default"))
        font_labels.addStretch()
        font_labels.addWidget(QLabel("Larger"))
        font_layout.addLayout(font_labels)
        
        appearance_layout.addWidget(font_group)
        
        # Add to card
        appearance_card.layout.addLayout(appearance_layout)
        
        # General settings placeholder
        general_card = Card("General Settings")
        general_card.layout.addWidget(QLabel("General settings coming soon..."))
        
        # Add settings pages to stack
        self.settings_stack.addWidget(appearance_card)
        self.settings_stack.addWidget(general_card)
        self.settings_stack.addWidget(QLabel("Notification settings coming soon..."))
        self.settings_stack.addWidget(QLabel("Backup & restore coming soon..."))
        self.settings_stack.addWidget(QLabel("About Smart Shop Manager v1.0"))
        
        # Add stack to right panel
        split.add_to_right(self.settings_stack)
        
        # Add split layout to page
        page_layout.add_widget(split)
    
    def on_category_changed(self, index):
        """Handle category selection"""
        self.settings_stack.setCurrentIndex(index)
    
    def on_theme_changed(self, theme_type):
        """Handle theme change"""
        # Theme is applied by the selector
        # We can add additional notifications or actions here
        pass

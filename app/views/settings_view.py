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
    QSlider, QColorDialog, QFileDialog, QMessageBox,
    QTabWidget, QLineEdit, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSettings, QSize
from PyQt5.QtGui import QFont, QIcon, QColor

from app.views.widgets.components import PageHeader, Card, Button, ComboBox
from app.views.widgets.layouts import SplitLayout, PageLayout
from app.utils.theme_manager import ThemeManager, ThemeType

import os
import sys
import json

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
    """Dedicated settings page for application configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the settings page UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Page header
        header = PageHeader("Application Settings", "Configure your application preferences")
        main_layout.addWidget(header)
        
        # Create scrollable area with responsive design
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Container for scrollable content
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # Appearance section
        appearance_card = Card("Appearance")
        appearance_form = QFormLayout()
        appearance_form.setSpacing(16)
        appearance_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        appearance_form.setLabelAlignment(Qt.AlignLeft)
        appearance_form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        
        # Create bold labels
        font_size_label = QLabel("Font Size:")
        font_size_label.setStyleSheet("font-weight: bold;")
        
        # Font size
        self.font_size_combo = ComboBox()
        self.font_size_combo.addItems(["Small", "Medium", "Large"])
        self.font_size_combo.setCurrentIndex(0)  # Default to small
        self.font_size_combo.setFixedHeight(35)
        self.font_size_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        appearance_form.addRow(font_size_label, self.font_size_combo)
        
        appearance_card.layout.addLayout(appearance_form)
        scroll_layout.addWidget(appearance_card)
        
        # Behavior section
        behavior_card = Card("Behavior")
        behavior_form = QFormLayout()
        behavior_form.setSpacing(16)
        behavior_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        behavior_form.setLabelAlignment(Qt.AlignLeft)
        behavior_form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        
        # Create bold labels
        autosave_label = QLabel("Auto-save Interval:")
        autosave_label.setStyleSheet("font-weight: bold;")
        
        remember_size_label = QLabel("Remember Window Size:")
        remember_size_label.setStyleSheet("font-weight: bold;")
        
        confirm_exit_label = QLabel("Confirm Exit:")
        confirm_exit_label.setStyleSheet("font-weight: bold;")
        
        # Auto-save interval with spinner and label aligned
        autosave_container = QWidget()
        autosave_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        autosave_layout = QHBoxLayout(autosave_container)
        autosave_layout.setContentsMargins(0, 0, 0, 0)
        autosave_layout.setSpacing(10)
        
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(1, 60)
        self.autosave_spin.setValue(10)
        self.autosave_spin.setFixedHeight(35)
        self.autosave_spin.setButtonSymbols(QSpinBox.UpDownArrows)
        self.autosave_spin.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        
        autosave_suffix = QLabel("minutes")
        autosave_suffix.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        autosave_layout.addWidget(self.autosave_spin)
        autosave_layout.addWidget(autosave_suffix)
        autosave_layout.addStretch()
        
        behavior_form.addRow(autosave_label, autosave_container)
        
        # Remember window size
        self.remember_size_check = QCheckBox()
        self.remember_size_check.setChecked(True)
        self.remember_size_check.setStyleSheet("margin-left: 3px;")
        behavior_form.addRow(remember_size_label, self.remember_size_check)
        
        # Confirm exit
        self.confirm_exit_check = QCheckBox()
        self.confirm_exit_check.setChecked(True)
        self.confirm_exit_check.setStyleSheet("margin-left: 3px;")
        behavior_form.addRow(confirm_exit_label, self.confirm_exit_check)
        
        behavior_card.layout.addLayout(behavior_form)
        scroll_layout.addWidget(behavior_card)
        
        # Data & Backup section
        backup_card = Card("Data & Backup")
        backup_form = QFormLayout()
        backup_form.setSpacing(16)
        backup_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        backup_form.setLabelAlignment(Qt.AlignLeft)
        backup_form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        
        # Create bold labels
        backup_dir_label = QLabel("Backup Directory:")
        backup_dir_label.setStyleSheet("font-weight: bold;")
        
        auto_backup_label = QLabel("Enable Auto-backup:")
        auto_backup_label.setStyleSheet("font-weight: bold;")
        
        backup_freq_label = QLabel("Backup Frequency:")
        backup_freq_label.setStyleSheet("font-weight: bold;")
        
        # Backup directory with browse button
        backup_container = QWidget()
        backup_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        backup_layout = QHBoxLayout(backup_container)
        backup_layout.setContentsMargins(0, 0, 0, 0)
        backup_layout.setSpacing(10)
        
        self.backup_path = QLineEdit()
        self.backup_path.setReadOnly(True)
        self.backup_path.setText("./backups")
        self.backup_path.setFixedHeight(35)
        self.backup_path.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        backup_browse_btn = Button("Browse")
        backup_browse_btn.setFixedHeight(35)
        backup_browse_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        backup_browse_btn.clicked.connect(self.select_backup_path)
        
        backup_layout.addWidget(self.backup_path)
        backup_layout.addWidget(backup_browse_btn)
        
        backup_form.addRow(backup_dir_label, backup_container)
        
        # Auto-backup
        self.auto_backup_check = QCheckBox()
        self.auto_backup_check.setChecked(True)
        self.auto_backup_check.setStyleSheet("margin-left: 3px;")
        backup_form.addRow(auto_backup_label, self.auto_backup_check)
        
        # Backup frequency
        self.backup_combo = ComboBox()
        self.backup_combo.addItems(["Daily", "Weekly", "Monthly"])
        self.backup_combo.setCurrentIndex(1)  # Default to weekly
        self.backup_combo.setFixedHeight(35)
        self.backup_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        backup_form.addRow(backup_freq_label, self.backup_combo)
        
        # Backup now button centered in its row
        backup_button_container = QWidget()
        backup_button_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        backup_button_layout = QHBoxLayout(backup_button_container)
        backup_button_layout.setContentsMargins(0, 10, 0, 0)
        
        backup_now_btn = Button("Backup Now", variant="primary")
        backup_now_btn.setFixedHeight(40)
        backup_now_btn.setMinimumWidth(150)
        backup_now_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        backup_now_btn.clicked.connect(self.backup_now)
        
        backup_button_layout.addWidget(backup_now_btn)
        backup_button_layout.addStretch()
        
        backup_form.addRow("", backup_button_container)
        
        backup_card.layout.addLayout(backup_form)
        scroll_layout.addWidget(backup_card)
        
        # User preferences section
        user_card = Card("User Preferences")
        user_form = QFormLayout()
        user_form.setSpacing(16)
        user_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        user_form.setLabelAlignment(Qt.AlignLeft)
        user_form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        
        # Create bold labels
        default_view_label = QLabel("Default View:")
        default_view_label.setStyleSheet("font-weight: bold;")
        
        notifications_label = QLabel("Enable Notifications:")
        notifications_label.setStyleSheet("font-weight: bold;")
        
        low_stock_label = QLabel("Low Stock Alert Threshold:")
        low_stock_label.setStyleSheet("font-weight: bold;")
        
        # Default view
        self.default_view_combo = ComboBox()
        self.default_view_combo.addItems(["Dashboard", "Inventory", "Sales", "Customers", "Reports"])
        self.default_view_combo.setCurrentIndex(0)  # Default to dashboard
        self.default_view_combo.setFixedHeight(35)
        self.default_view_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        user_form.addRow(default_view_label, self.default_view_combo)
        
        # Notification settings
        self.notifications_check = QCheckBox()
        self.notifications_check.setChecked(True)
        self.notifications_check.setStyleSheet("margin-left: 3px;")
        user_form.addRow(notifications_label, self.notifications_check)
        
        # Low stock threshold with spinner and suffix
        stock_container = QWidget()
        stock_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        stock_layout = QHBoxLayout(stock_container)
        stock_layout.setContentsMargins(0, 0, 0, 0)
        stock_layout.setSpacing(10)
        
        self.low_stock_spin = QSpinBox()
        self.low_stock_spin.setRange(1, 100)
        self.low_stock_spin.setValue(13)
        self.low_stock_spin.setFixedHeight(35)
        self.low_stock_spin.setButtonSymbols(QSpinBox.UpDownArrows)
        self.low_stock_spin.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        
        stock_suffix = QLabel("items")
        stock_suffix.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        stock_layout.addWidget(self.low_stock_spin)
        stock_layout.addWidget(stock_suffix)
        stock_layout.addStretch()
        
        user_form.addRow(low_stock_label, stock_container)
        
        user_card.layout.addLayout(user_form)
        scroll_layout.addWidget(user_card)
        
        # Buttons in a responsive container
        buttons_container = QWidget()
        buttons_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 20, 0, 10)
        
        # Add stretches for responsive layout
        buttons_layout.addStretch(1)
        
        self.reset_btn = Button("Reset to Defaults", variant="secondary")
        self.reset_btn.setFixedHeight(40)
        self.reset_btn.setMinimumWidth(150)
        self.reset_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_btn)
        
        buttons_layout.addSpacing(15)
        
        self.save_btn = Button("Save Settings", variant="primary")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_btn)
        
        scroll_layout.addWidget(buttons_container)
        scroll_layout.addStretch()
        
        # Finish scroll area setup
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def load_settings(self):
        """Load settings from the config file"""
        try:
            # Import the settings module
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
            from config import settings
            
            # Set font size
            font_size_map = {
                "small": 0,
                "medium": 1,
                "large": 2
            }
            self.font_size_combo.setCurrentIndex(font_size_map.get(settings.FONT_SIZE, 0))
            
            # Set behavior settings
            self.autosave_spin.setValue(settings.AUTO_SAVE_INTERVAL)
            self.remember_size_check.setChecked(settings.REMEMBER_WINDOW_SIZE)
            self.confirm_exit_check.setChecked(settings.CONFIRM_EXIT)
            
            # Set backup settings
            self.backup_path.setText(settings.LOCAL_BACKUP_PATH)
            self.auto_backup_check.setChecked(settings.AUTO_BACKUP_ENABLED)
            
            backup_freq_map = {
                "daily": 0,
                "weekly": 1,
                "monthly": 2
            }
            self.backup_combo.setCurrentIndex(backup_freq_map.get(settings.BACKUP_FREQUENCY, 1))
            
            # Set user preferences
            view_map = {
                "dashboard": 0,
                "inventory": 1,
                "sales": 2,
                "customers": 3,
                "reports": 4
            }
            self.default_view_combo.setCurrentIndex(view_map.get(settings.DEFAULT_VIEW, 0))
            self.notifications_check.setChecked(settings.NOTIFICATIONS_ENABLED)
            self.low_stock_spin.setValue(settings.LOW_STOCK_THRESHOLD)
            
        except (ImportError, AttributeError) as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to the config file"""
        try:
            # Get the settings file path
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
            from config import settings
            settings_path = os.path.join(os.path.dirname(settings.__file__), 'settings.py')
            
            # Read the current settings file
            with open(settings_path, 'r') as f:
                content = f.read()
            
            # Font size map
            font_map = {
                0: "small",
                1: "medium",
                2: "large"
            }
            font_size = font_map.get(self.font_size_combo.currentIndex(), "small")
            
            # Backup frequency map
            backup_map = {
                0: "daily",
                1: "weekly",
                2: "monthly"
            }
            backup_freq = backup_map.get(self.backup_combo.currentIndex(), "weekly")
            
            # View map
            view_map = {
                0: "dashboard",
                1: "inventory",
                2: "sales",
                3: "customers",
                4: "reports"
            }
            default_view = view_map.get(self.default_view_combo.currentIndex(), "dashboard")
            
            # Update settings values
            replacements = [
                ('FONT_SIZE = ".*"', f'FONT_SIZE = "{font_size}"'),
                ('AUTO_SAVE_INTERVAL = \\d+', f'AUTO_SAVE_INTERVAL = {self.autosave_spin.value()}'),
                ('REMEMBER_WINDOW_SIZE = (?:True|False)', f'REMEMBER_WINDOW_SIZE = {self.remember_size_check.isChecked()}'),
                ('CONFIRM_EXIT = (?:True|False)', f'CONFIRM_EXIT = {self.confirm_exit_check.isChecked()}'),
                ('LOCAL_BACKUP_PATH = ".*"', f'LOCAL_BACKUP_PATH = "{self.backup_path.text()}"'),
                ('AUTO_BACKUP_ENABLED = (?:True|False)', f'AUTO_BACKUP_ENABLED = {self.auto_backup_check.isChecked()}'),
                ('BACKUP_FREQUENCY = ".*"', f'BACKUP_FREQUENCY = "{backup_freq}"'),
                ('DEFAULT_VIEW = ".*"', f'DEFAULT_VIEW = "{default_view}"'),
                ('NOTIFICATIONS_ENABLED = (?:True|False)', f'NOTIFICATIONS_ENABLED = {self.notifications_check.isChecked()}'),
                ('LOW_STOCK_THRESHOLD = \\d+', f'LOW_STOCK_THRESHOLD = {self.low_stock_spin.value()}')
            ]
            
            # Apply all replacements
            import re
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            # Write back to the file
            with open(settings_path, 'w') as f:
                f.write(content)
            
            QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
            
            # Apply changes immediately
            if hasattr(self.parent_window, 'show_alert'):
                self.parent_window.show_alert("Settings saved successfully! Some changes may require restarting the application.", "success")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        response = QMessageBox.question(
            self, "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if response == QMessageBox.Yes:
            self.font_size_combo.setCurrentIndex(0)  # Small
            self.autosave_spin.setValue(10)
            self.remember_size_check.setChecked(True)
            self.confirm_exit_check.setChecked(True)
            self.backup_path.setText("./backups")
            self.auto_backup_check.setChecked(True)
            self.backup_combo.setCurrentIndex(1)  # Weekly
            self.default_view_combo.setCurrentIndex(0)  # Dashboard
            self.notifications_check.setChecked(True)
            self.low_stock_spin.setValue(13)
            
            QMessageBox.information(self, "Settings Reset", "Settings have been reset to defaults.")
    
    def on_theme_changed(self, index):
        """Theme change is not supported anymore - only Light theme is available"""
        pass
    
    def select_backup_path(self):
        """Open file dialog to select backup directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Backup Directory", 
            self.backup_path.text(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:
            self.backup_path.setText(directory)
    
    def backup_now(self):
        """Perform immediate backup"""
        # This would call the appropriate backup function
        QMessageBox.information(
            self, 
            "Backup Started",
            f"Backup process started to directory:\n{self.backup_path.text()}\n\nThis may take a few moments."
        )

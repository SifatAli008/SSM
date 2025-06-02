"""
Smart Shop Manager - Layout Components
File: app/views/widgets/layouts.py

This module provides standardized layout components to ensure
consistent page structure throughout the application.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QSizePolicy, QSpacerItem, QFrame, QStackedWidget, QPushButton
)
from PyQt5.QtCore import Qt

try:
    from app.utils.theme_manager import ThemeManager
except ImportError:
    # Fallback if theme manager is not available
    from ..utils.theme_manager import ThemeManager

class PageLayout(QWidget):
    """
    Standard page layout with header and content area
    
    Structure:
    - Header (title, actions)
    - Content
    - Optional footer
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Header container
        self.header_container = QWidget()
        self.header_layout = QVBoxLayout(self.header_container)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Content container with scroll support
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.content_container)
        
        # Footer container (optional)
        self.footer_container = QWidget()
        self.footer_container.setVisible(False)
        self.footer_layout = QHBoxLayout(self.footer_container)
        self.footer_layout.setContentsMargins(0, 20, 0, 0)
        
        # Add components to main layout
        self.layout.addWidget(self.header_container)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.footer_container)
    
    def set_header(self, header_widget):
        """Set the page header"""
        # Clear existing header
        for i in reversed(range(self.header_layout.count())):
            item = self.header_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new header
        self.header_layout.addWidget(header_widget)
    
    def add_widget(self, widget):
        """Add a widget to the content area"""
        self.content_layout.addWidget(widget)
    
    def clear_content(self):
        """Clear all widgets from the content area"""
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
    
    def set_footer(self, visible=True):
        """Show or hide the footer"""
        self.footer_container.setVisible(visible)
    
    def add_footer_widget(self, widget, alignment=None):
        """Add a widget to the footer"""
        if alignment:
            self.footer_layout.addWidget(widget, 0, alignment)
        else:
            self.footer_layout.addWidget(widget)
    
    def add_footer_spacer(self):
        """Add a flexible spacer to the footer"""
        self.footer_layout.addStretch()

class CardGrid(QWidget):
    """
    Grid layout for card widgets with responsive behavior
    
    This component automatically arranges cards in a grid
    that adapts to the available space.
    """
    
    def __init__(self, columns=2, parent=None):
        super().__init__(parent)
        
        self.columns = columns
        
        # Grid layout
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(20)
        
        # Current position
        self.current_row = 0
        self.current_col = 0
    
    def add_card(self, card):
        """Add a card to the grid"""
        self.layout.addWidget(card, self.current_row, self.current_col)
        
        # Update position for next card
        self.current_col += 1
        if self.current_col >= self.columns:
            self.current_col = 0
            self.current_row += 1

class SplitLayout(QWidget):
    """
    Two-column layout with adjustable sizes
    
    This component creates a split view with two side-by-side panels.
    """
    
    def __init__(self, left_proportion=1, right_proportion=1, parent=None):
        super().__init__(parent)
        
        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(20)
        
        # Left panel
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Right panel
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add panels to main layout with proportions
        self.layout.addWidget(self.left_container, left_proportion)
        self.layout.addWidget(self.right_container, right_proportion)
    
    def add_to_left(self, widget):
        """Add a widget to the left panel"""
        self.left_layout.addWidget(widget)
    
    def add_to_right(self, widget):
        """Add a widget to the right panel"""
        self.right_layout.addWidget(widget)
    
    def clear_left(self):
        """Clear all widgets from the left panel"""
        for i in reversed(range(self.left_layout.count())):
            item = self.left_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
    
    def clear_right(self):
        """Clear all widgets from the right panel"""
        for i in reversed(range(self.right_layout.count())):
            item = self.right_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

class TabsLayout(QWidget):
    """
    Stacked widget layout with tab navigation
    
    This component creates a custom tab interface using buttons
    for navigation and a stacked widget for content.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(20)
        
        # Tabs container
        self.tabs_container = QWidget()
        self.tabs_layout = QHBoxLayout(self.tabs_container)
        self.tabs_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs_layout.setSpacing(5)
        
        # Content stack
        self.stack = QStackedWidget()
        
        # Add components to main layout
        self.layout.addWidget(self.tabs_container)
        self.layout.addWidget(self.stack)
        
        # Tab buttons
        self.tab_buttons = []
    
    def add_tab(self, title, widget):
        """
        Add a tab with content
        
        Args:
            title (str): Tab title
            widget (QWidget): Content widget
        """
        # Create tab button
        tab_button = QPushButton(title)
        tab_button.setCheckable(True)
        tab_button.setCursor(Qt.PointingHandCursor)
        tab_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-bottom: 3px solid transparent;
                background-color: transparent;
                font-weight: normal;
                color: #111;
            }
            QPushButton:checked {
                border-bottom: 3px solid #3498db;
                color: #111;
                font-weight: bold;
            }
        """)
        
        index = len(self.tab_buttons)
        tab_button.clicked.connect(lambda: self.select_tab(index))
        
        self.tabs_layout.addWidget(tab_button)
        self.tab_buttons.append(tab_button)
        
        # Add content to stack
        self.stack.addWidget(widget)
        
        # Select first tab by default
        if len(self.tab_buttons) == 1:
            self.select_tab(0)
    
    def select_tab(self, index):
        """
        Select a tab by index
        
        Args:
            index (int): Tab index
        """
        # Update button states
        for i, button in enumerate(self.tab_buttons):
            button.setChecked(i == index)
        
        # Update stack
        self.stack.setCurrentIndex(index)
    
    def current_index(self):
        """Get the index of the current tab"""
        return self.stack.currentIndex()

class DashboardLayout(QWidget):
    """
    Dashboard layout with summary cards and detail sections
    
    This component creates a dashboard with summary cards at the top
    and detail sections below.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(30)
        
        # Summary cards area
        self.summary_container = QWidget()
        self.summary_grid = QGridLayout(self.summary_container)
        self.summary_grid.setContentsMargins(0, 0, 0, 0)
        self.summary_grid.setSpacing(20)
        
        # Current position for summary cards
        self.current_row = 0
        self.current_col = 0
        self.columns = 3
        
        # Details area (can contain multiple sections)
        self.details_container = QWidget()
        self.details_layout = QVBoxLayout(self.details_container)
        self.details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_layout.setSpacing(30)
        
        # Add components to main layout
        self.layout.addWidget(self.summary_container)
        self.layout.addWidget(self.details_container)
    
    def add_summary_card(self, card):
        """Add a summary card to the grid"""
        self.summary_grid.addWidget(card, self.current_row, self.current_col)
        
        # Update position for next card
        self.current_col += 1
        if self.current_col >= self.columns:
            self.current_col = 0
            self.current_row += 1
    
    def add_detail_section(self, widget):
        """Add a detail section to the dashboard"""
        self.details_layout.addWidget(widget)
    
    def set_columns(self, columns):
        """Set the number of columns for summary cards"""
        self.columns = columns 
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

from app.utils.theme_manager import ThemeManager, ThemeType
from app.views.widgets.components import TableComponent, Card

class TableTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Apply light theme
        ThemeManager.apply_theme(ThemeType.LIGHT)
        
        self.setWindowTitle("Table Edit Test")
        self.setMinimumSize(800, 500)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create a card to contain the table
        card = Card("Editable Table Example")
        card_layout = QVBoxLayout()
        
        # Create our enhanced table
        self.table = TableComponent()
        self.table.setup_columns(["ID", "Product", "Price", "Stock"])
        
        # Add some sample data
        test_data = [
            [1, "Product 1", "$10.99", 100],
            [2, "Product 2", "$21.98", 50],
            [3, "Product 3", "$32.97", 75],
            [4, "Product 4", "$43.96", 25],
            [5, "Product 5", "$54.95", 10]
        ]
        
        for row_data in test_data:
            self.table.add_row(row_data)
        
        # Make the table editable
        self.table.setEditTriggers(TableComponent.DoubleClicked | TableComponent.EditKeyPressed)
        
        card_layout.addWidget(self.table)
        card.layout.addLayout(card_layout)
        
        # Buttons 
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Row")
        add_button.clicked.connect(self.add_row)
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_selected)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        
        main_layout.addWidget(card)
        main_layout.addLayout(button_layout)
    
    def add_row(self):
        next_id = self.table.rowCount() + 1
        self.table.add_row([next_id, f"New Product {next_id}", f"${next_id * 10.99:.2f}", 0])
    
    def delete_selected(self):
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TableTestWindow()
    window.show()
    sys.exit(app.exec_()) 
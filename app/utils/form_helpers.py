from PyQt5.QtWidgets import QLineEdit, QComboBox
from dataclasses import dataclass


def get_widget_text(widget):
    if isinstance(widget, QLineEdit):
        return widget.text()
    elif isinstance(widget, QComboBox):
        return widget.currentText()
    else:
        raise TypeError("Unsupported widget type")

@dataclass
class ProductData:
    name: str
    quantity: int
    price: float
    category: str

def validate_product_data(product: ProductData):
    if not product.name.strip():
        return False, "Product name cannot be empty."
    if product.quantity < 0:
        return False, "Quantity must be non-negative."
    if product.price < 0:
        return False, "Price must be non-negative."
    if not product.category.strip():
        return False, "Category cannot be empty."
    return True, "" 
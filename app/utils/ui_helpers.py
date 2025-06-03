from PyQt5.QtWidgets import QMessageBox

def show_error(parent, message, title="Error"):
    QMessageBox.critical(parent, title, message) 
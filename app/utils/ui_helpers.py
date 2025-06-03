from PyQt5.QtWidgets import QMessageBox
from app.utils.logger import Logger

def show_error(parent, message, title="Error"):
    Logger().error(f"UI Error Dialog - {title}: {message}")
    QMessageBox.critical(parent, title, message) 
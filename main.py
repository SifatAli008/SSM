import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from app.utils.logger import logger
from app.utils.config_manager import config_manager
from app.utils.database import DatabaseManager
from app.ui.main_window import MainWindow
from app.core.auth import AuthManager
from app.core.event_system import EventSystem
from app.core.backup import BackupManager
from app.core.reports import ReportManager
from app.core.inventory import InventoryManager
from app.core.sales import SalesManager
from app.core.users import UserManager

class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_application()
        self.initialize_managers()
        self.setup_main_window()
        
    def setup_application(self):
        """Set up application-wide settings."""
        # Set application name and version
        self.app.setApplicationName(config_manager.get('app.name'))
        self.app.setApplicationVersion(config_manager.get('app.version'))
        
        # Set application style
        self.app.setStyle('Fusion')
        
        # Enable high DPI scaling
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        logger.info("Application initialized")
    
    def initialize_managers(self):
        """Initialize all manager components."""
        try:
            # Initialize database first
            self.db_manager = DatabaseManager()
            
            # Initialize event system
            self.event_system = EventSystem()
            
            # Initialize other managers
            self.auth_manager = AuthManager()
            self.backup_manager = BackupManager(self.event_system)
            self.report_manager = ReportManager()
            self.inventory_manager = InventoryManager()
            self.sales_manager = SalesManager()
            self.user_manager = UserManager()
            
            logger.info("All managers initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize managers: {e}")
            sys.exit(1)
    
    def setup_main_window(self):
        """Set up and show the main window."""
        try:
            self.main_window = MainWindow(
                auth_manager=self.auth_manager,
                event_system=self.event_system,
                backup_manager=self.backup_manager,
                report_manager=self.report_manager,
                inventory_manager=self.inventory_manager,
                sales_manager=self.sales_manager,
                user_manager=self.user_manager
            )
            self.main_window.show()
            logger.info("Main window initialized and displayed")
        except Exception as e:
            logger.error(f"Failed to initialize main window: {e}")
            sys.exit(1)
    
    def run(self):
        """Run the application."""
        try:
            # Start backup manager if enabled
            if config_manager.get('backup.enabled'):
                self.backup_manager.start_auto_backup()
            
            # Start event system
            self.event_system.start()
            
            # Run the application
            return self.app.exec_()
        except Exception as e:
            logger.error(f"Application runtime error: {e}")
            return 1
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources before exit."""
        try:
            # Stop event system
            self.event_system.stop()
            
            # Stop backup manager
            if config_manager.get('backup.enabled'):
                self.backup_manager.stop_auto_backup()
            
            # Close database connections
            if hasattr(self, 'db_manager'):
                self.db_manager.engine.dispose()
            
            logger.info("Application cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

def main():
    """Main entry point of the application."""
    try:
        app = Application()
        return app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
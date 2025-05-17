#!/usr/bin/env python3
import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from app.views.main_window import MainWindow
from app.utils.logger import logger
from app.utils.event_system import global_event_system
from app.utils.cache_manager import global_cache

def configure_debug_mode():
    """
    Configure the application for debug mode:
    - Set up detailed logging
    - Enable event system debugging
    - Configure cache with shorter TTLs
    """
    # Update logging level for the console output
    # Our logger is a custom implementation that already has handlers
    # No need to add handlers, just change the log level
    logging.getLogger("SmartShopManager").setLevel(logging.DEBUG)
    
    # Enable event system debugging
    global_event_system.set_debug_mode(True)
    logger.info("[DEBUG] Debug mode enabled - Event system debugging active")
    
    # Set up debug environment variables
    os.environ["SSM_DEBUG"] = "1"
    os.environ["SSM_CACHE_TTL"] = "60"  # 1 minute cache in debug mode
    
    logger.info("[CONFIG] Debug configuration complete")

def print_debug_summary():
    """Print a summary of debug information"""
    logger.info("==== Smart Shop Manager Debug Mode ====")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"PyQt5 version: {QApplication.instance().applicationVersion()}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Print cache stats
    try:
        stats = global_cache.get_stats()
        logger.info(f"Cache statistics: {stats}")
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
    
    logger.info("======================================")

def run_debug():
    """
    Run the application in debug mode with additional debug features.
    This includes automatic login and debug logging.
    """
    # Set up the debug environment
    configure_debug_mode()
    
    # Create and start the application
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Shop Manager - DEBUG MODE")
    app.setApplicationVersion("1.0-dev")
    
    # Print debug summary
    print_debug_summary()
    
    # Create a test user for automatic login
    from app.models.users import User
    debug_user = User(
        username="debug_user",
        password="password",
        full_name="Debug User",
        role="admin",
        is_active=True
    )
    
    # Create and show the main window with the debug user
    window = MainWindow(debug_user)
    window.setWindowTitle(window.windowTitle() + " [DEBUG MODE]")
    window.show()
    
    # Start the event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_debug() 
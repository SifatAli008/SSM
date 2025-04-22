"""
Smart Shop Manager - Global Stylesheet
File: views/styles.py

This file contains global stylesheet definitions for the Smart Shop Manager app.
Import and apply these styles to maintain consistent appearance across the application.
"""

def get_application_stylesheet():
    """
    Returns the global application stylesheet
    """
    return """
    QMainWindow {
        background-color: #f5f7fa;
    }
    
    #sidebar {
        background-color: #2c3e50;
        color: white;
        border: none;
    }
    
    #header {
        background-color: white;
        border-bottom: 1px solid #e0e0e0;
    }
    
    #searchContainer {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 20px;
    }
    
    #searchInput {
        border: none;
        background: transparent;
    }
    
    #notificationBtn {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 15px;
    }
    
    #adminBtn {
        background-color: white;
        color: #333;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 8px 15px;
    }
    
    #turnOffBtn {
        background-color: #e74c3c;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 15px;
    }
    
    #card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #e0e0e0;
    }
    
    #cardTitle {
        color: #7f8c8d;
        font-size: 14px;
    }
    
    #cardValue {
        color: #2c3e50;
        margin-top: 5px;
    }
    
    #cardSubtitle {
        color: #7f8c8d;
        margin-top: 5px;
    }
    
    #alertBar {
        background-color: #b19cd9;
        color: #4a235a;
    }
    
    #footer {
        background-color: white;
        border-top: 1px solid #e0e0e0;
        color: #7f8c8d;
    }
    """
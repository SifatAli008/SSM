# Smart Shop Manager

A comprehensive desktop application for retail store management built with Python and PyQt5. The application provides a modern, responsive UI with intuitive controls for managing inventory, sales, customers, and generating reports.

## Recent Improvements
- **Full migration to Firebase for inventory:** All inventory operations (CRUD, analytics, categories) are now live-synced with Firebase Realtime Database for real-time, cloud-based management
- Removed all SQL/SQLite logic from inventory management for a fully cloud-native backend
- Unified info card backgrounds and value text for a seamless, professional look
- Inventory info cards now always show up-to-date values (never blank)
- Modernized search bar in inventory view for better usability and appearance
- Improved real-time updates for all dashboard and inventory metrics
- Enhanced UI consistency and accessibility across all views

## Features

### Sales Dashboard
- Real-time sales metrics and analytics
- Daily, weekly, and monthly sales overview
- **Modern, visually enhanced charts** (line, bar, flow)
- **Click any dashboard graph to open a full interactive Plotly chart in your browser**
- Performance indicators and quick access to common actions

### Inventory Management
- Complete product tracking and management
- **Live cloud sync with Firebase Realtime Database**
- Barcode scanning support
- Low stock alerts
- Category management with custom categories
- CSV export functionality

### Sales Processing
- Fast and intuitive sales interface
- Customer management
- Receipt generation
- Multiple payment methods

### Reporting & Analytics
- Comprehensive financial reports
- Inventory valuation reports
- Sales trend analysis
- Profit margin calculation
- Printable report generation
- **Quarterly profit chart is robust and always displays all quarters**

### User Management
- Secure login system
- Role-based access control
- User activity tracking

## Technical Features

### Modern Architecture
- **Event-driven architecture** for real-time data updates across components
- **Data caching system** for improved performance
- Comprehensive **automated testing** framework
- Clean **MVC design pattern** for separation of concerns

### UI Features
- Consistent styling and component design across all pages
- Standardized button styling with action-based colors
- Responsive layouts that adapt to different screen sizes
- Improved text readability with appropriate font sizes and contrast
- Intuitive navigation and user workflow
- **Unified info card backgrounds and value text for a seamless look**
- **Inventory info cards always show up-to-date values**
- **Modern, polished search bar in inventory view**
- **Enhanced graph visuals and interactivity**

## Technical Information

- Built with Python 3.9+ and PyQt5
- Uses Plotly for interactive charting (opens in browser)
- **Firebase Realtime Database for all inventory data operations**
- MVC architecture for clean separation of concerns
- PDF generation for reports and receipts
- Event-based communication system for real-time updates
- Performance optimization with data caching
- Comprehensive test suite

## Automated Testing & UI Test Reliability

- The test suite now includes robust UI tests for all major workflows, including inventory add/edit dialogs.
- UI tests use a `test_mode` flag and patch modal dialogs (like `ProductDialog`) to simulate user input and auto-accept, ensuring tests are reliable and deterministic.
- No production code logic is changed for testing—tests patch dialogs at runtime for clean separation.
- See `tests/test_ui.py` for examples of dialog patching and best practices for PyQt5 UI automation.

## Getting Started

### Prerequisites
- Python 3.9 or higher
- PyQt5
- Plotly
- **Firebase account and configuration for Realtime Database**
- Other dependencies in requirements.txt

### Installation
1. Clone the repository
```bash
git clone https://github.com/SifatAli008/SSM.git
```

2. Create and activate a virtual environment (recommended)
```bash
# Create venv (if not already present)
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate

# Activate venv (macOS/Linux)
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure Firebase
- Set up your Firebase project and Realtime Database
- Add your Firebase configuration to the app (see `config/` or documentation)

5. Run the application
```bash
python run.py
```

### Testing
Run the automated test suite to ensure everything is working properly:
```bash
python run_tests.py
```

All UI and backend tests should pass. If you add new dialogs or UI forms, follow the same patching pattern for reliable automation.

### Troubleshooting
- If you see errors about missing packages, make sure your virtual environment is activated before running `pip install` or `python run.py`.
- If you have issues with PyQt5 on Linux, you may need to install system dependencies (see PyQt5 docs).
- For Firebase issues, ensure your configuration is correct and the Realtime Database is enabled.

## Documentation

For more detailed documentation about specific components:

- [Event System Documentation](README_EVENT_SYSTEM.md) - Details about the real-time event system
- [API Reference](docs/API.md) - API documentation for developers
- [User Guide](docs/USER_GUIDE.md) - Comprehensive guide for users

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For more, see the [GitHub repository](https://github.com/SifatAli008/SSM)
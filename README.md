# Smart Shop Manager (SSM)

A Python-based desktop application designed to streamline business operations by optimizing inventory management, sales tracking, and customer insights with AI-powered business improvement suggestions.

## Features

- Business Improvement Insights (AI-powered analysis)
- Inventory Management
- Sales & Billing System
- Customer & Supplier Management
- Reporting & Analytics
- Security & Multi-User Access
- Backup & Data Recovery

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure database settings in `config/database.py`

5. Run the application:
   ```
   python run.py
   ```

## Technology Stack

- Python with PyQt5 for GUI
- MySQL (Cloud-based)
- SQLAlchemy ORM
- Pandas & Scikit-learn for Analytics
- ReportLab for PDF generation

## Project Structure

The project follows an MVC (Model-View-Controller) architecture:
- `models/`: Database models
- `views/`: UI components
- `controllers/`: Business logic
- `utils/`: Helper functions and utilities

## Development Guidelines

- Follow PEP 8 style guidelines
- Write unit tests for new features
- Document code with docstrings
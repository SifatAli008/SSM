# Smart Shop Manager API Documentation

## Overview

This document provides detailed information about the Smart Shop Manager's API endpoints, data models, and integration points.

## Core Components

### Database Models

#### Inventory
```python
class Inventory:
    def create(name: str, quantity: int, price: float, category: str) -> Product
    def get_by_name(name: str) -> Product
    def update(id: int, **kwargs) -> bool
    def delete(id: int) -> bool
    def get_all() -> List[Product]
    def get_by_category(category: str) -> List[Product]
```

#### Sales
```python
class Sales:
    def create(items: List[Dict], customer_id: int, total_amount: float) -> Sale
    def get_by_id(id: int) -> Sale
    def get_by_date_range(start_date: str, end_date: str) -> List[Sale]
    def get_by_customer(customer_id: int) -> List[Sale]
```

#### Users
```python
class User:
    def create(username: str, password: str, role: str) -> User
    def get_by_username(username: str) -> User
    def verify_password(password: str) -> bool
    def update(id: int, **kwargs) -> bool
```

#### Customers
```python
class Customer:
    def create(name: str, email: str, phone: str) -> Customer
    def get_by_email(email: str) -> Customer
    def update(id: int, **kwargs) -> bool
    def get_all() -> List[Customer]
```

### Controllers

#### InventoryController
```python
class InventoryController:
    def add_product(name: str, quantity: int, price: float, category: str) -> bool
    def update_product(name: str, **kwargs) -> bool
    def delete_product(name: str) -> bool
    def get_product(name: str) -> Product
    def get_all_products() -> List[Product]
    def get_low_stock_products(threshold: int = 10) -> List[Product]
```

#### SalesController
```python
class SalesController:
    def create_sale(items: List[Dict], customer_id: int, total_amount: float) -> int
    def get_sale(id: int) -> Sale
    def get_sales_by_date_range(start_date: str, end_date: str) -> List[Sale]
    def get_sales_by_customer(customer_id: int) -> List[Sale]
    def get_daily_sales(date: str) -> float
    def get_monthly_sales(year: int, month: int) -> float
```

#### UserController
```python
class UserController:
    def create_user(username: str, password: str, role: str) -> bool
    def authenticate(username: str, password: str) -> bool
    def get_user(username: str) -> User
    def update_user(username: str, **kwargs) -> bool
    def delete_user(username: str) -> bool
```

#### ReportController
```python
class ReportController:
    def generate_sales_report(start_date: str, end_date: str) -> Dict
    def generate_inventory_report() -> Dict
    def generate_customer_report() -> Dict
    def generate_profit_report(start_date: str, end_date: str) -> Dict
```

### Event System

The event system provides real-time updates across the application:

```python
class EventSystem:
    # Signals
    inventory_updated = Signal()
    sales_updated = Signal()
    customer_updated = Signal()
    reports_updated = Signal()
    settings_updated = Signal()
    
    # Methods
    def notify_inventory_update()
    def notify_sales_update()
    def notify_customer_update()
    def notify_reports_update()
    def notify_settings_update()
```

## Data Types

### Product
```python
class Product:
    id: int
    name: str
    quantity: int
    price: float
    category: str
    created_at: datetime
    updated_at: datetime
```

### Sale
```python
class Sale:
    id: int
    items: List[Dict]
    customer_id: int
    total_amount: float
    created_at: datetime
```

### User
```python
class User:
    id: int
    username: str
    password_hash: str
    role: str
    created_at: datetime
    last_login: datetime
```

### Customer
```python
class Customer:
    id: int
    name: str
    email: str
    phone: str
    created_at: datetime
    updated_at: datetime
```

## Error Handling

The API uses standard HTTP status codes and returns error messages in the following format:

```python
{
    "error": {
        "code": int,
        "message": str,
        "details": Dict
    }
}
```

Common error codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Security

### Authentication
- All API endpoints require authentication except for login
- JWT tokens are used for authentication
- Tokens expire after 24 hours

### Authorization
- Role-based access control (RBAC)
- Available roles: admin, manager, staff
- Each role has specific permissions

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per user
- Rate limit headers are included in responses

## Best Practices

1. Always handle errors appropriately
2. Use proper authentication headers
3. Implement proper input validation
4. Follow RESTful principles
5. Use appropriate HTTP methods
6. Implement proper logging
7. Follow security best practices

## Examples

### Creating a Product
```python
# Using the API
response = inventory_controller.add_product(
    name="Test Product",
    quantity=10,
    price=99.99,
    category="Electronics"
)

# Using the Model
product = inventory_model.create(
    name="Test Product",
    quantity=10,
    price=99.99,
    category="Electronics"
)
```

### Creating a Sale
```python
# Using the API
sale_id = sales_controller.create_sale(
    items=[{"product_id": 1, "quantity": 2, "price": 99.99}],
    customer_id=1,
    total_amount=199.98
)

# Using the Model
sale = sales_model.create(
    items=[{"product_id": 1, "quantity": 2, "price": 99.99}],
    customer_id=1,
    total_amount=199.98
)
```

## Integration

### Database
- SQLite for development
- MySQL for production
- Connection string format: `mysql://user:password@host:port/database`

### External Services
- Firebase for authentication
- SMTP for email notifications
- AWS S3 for file storage

## Versioning

The API is versioned using the following format:
- Major version: Breaking changes
- Minor version: New features
- Patch version: Bug fixes

Current version: 1.0.0 
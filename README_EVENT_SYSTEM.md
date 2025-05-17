# Smart Shop Manager Event System

## Overview

The Smart Shop Manager application uses a centralized event system to ensure real-time data synchronization across different views and components. This system enables various parts of the application to communicate with each other when data changes, without direct coupling.

## How It Works

1. **Event System Core** (`app/utils/event_system.py`):
   - Implements a singleton class with PyQt5 signals
   - Provides global access through `global_event_system`
   - Defines specific signals for different data types (inventory, sales, customers, etc.)

2. **Controller Integration**:
   - Controllers emit signals when data changes (CRUD operations)
   - Example: When a product is added, `notify_inventory_update()` is called

3. **View Integration**:
   - Views connect to signals to receive real-time updates
   - Each view implements a `refresh_data()` method to update UI components
   - Views refresh relevant data only when the corresponding signal is emitted

## Signal Types

The event system supports the following signals:

- `inventory_updated` - Emitted when inventory data changes
- `sales_updated` - Emitted when sales data changes
- `customer_updated` - Emitted when customer data changes
- `reports_updated` - Emitted when reports are generated
- `settings_updated` - Emitted when settings change

## Usage Examples

### Emitting Events (Controllers)

```python
# In a controller method
def add_product(self, name, quantity, price):
    # Add product to database
    result = self.model.add(name, quantity, price)
    
    # Notify the system about the change
    if result:
        global_event_system.notify_inventory_update()
    
    return result
```

### Listening for Events (Views)

```python
# In a view class
def setup_event_listeners(self):
    # Connect to the inventory update signal
    global_event_system.inventory_updated.connect(self.refresh_data)

def refresh_data(self):
    # Update UI components with fresh data
    self.load_data_from_controller()
    self.update_summary_cards()
```

## Benefits of the Event System

1. **Real-time Updates** - Data changes are immediately reflected across all views
2. **Decoupled Architecture** - Components communicate without direct dependencies
3. **Consistent State** - All parts of the application stay in sync with the database
4. **Enhanced User Experience** - Users see current data without manual refreshing

## Implementation Guidelines

When adding new features:

1. **New Data Types** - Add new signals in the event system if needed
2. **Controller Changes** - Always emit appropriate signals after data modifications
3. **View Integration** - Implement `refresh_data()` in new views to handle updates
4. **Performance** - Be mindful of update frequency to avoid excessive UI refreshes

## Troubleshooting

If real-time updates are not working:

1. Ensure the controller is emitting the correct signal
2. Verify the view is connected to the right signal
3. Check that the `refresh_data()` method properly updates all UI components
4. Monitor the console for any error messages during the update process 
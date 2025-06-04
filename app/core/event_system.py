from typing import Dict, List, Callable, Any
from datetime import datetime
from threading import Thread, Event
from queue import Queue
import time
from app.utils.logger import Logger

logger = Logger()

class EventSystem:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_queue = Queue()
        self._stop_event = Event()
        self._worker_thread = None
    
    def start(self):
        """Start the event processing thread."""
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._stop_event.clear()
            self._worker_thread = Thread(target=self._process_events, daemon=True)
            self._worker_thread.start()
            logger.info("Event system started")
    
    def stop(self):
        """Stop the event processing thread."""
        if self._worker_thread and self._worker_thread.is_alive():
            self._stop_event.set()
            self._worker_thread.join()
            logger.info("Event system stopped")
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
            logger.debug(f"Unsubscribed from event: {event_type}")
    
    def publish(self, event_type: str, data: Any = None):
        """Publish an event."""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow()
        }
        self._event_queue.put(event)
        logger.debug(f"Published event: {event_type}")
    
    def _process_events(self):
        """Process events in the queue."""
        while not self._stop_event.is_set():
            try:
                # Get event from queue with timeout
                event = self._event_queue.get(timeout=1)
                
                # Process event
                event_type = event['type']
                if event_type in self._handlers:
                    for handler in self._handlers[event_type]:
                        try:
                            handler(event['data'])
                        except Exception as e:
                            logger.error(f"Error in event handler for {event_type}: {e}")
                
                self._event_queue.task_done()
            except Exception as e:
                if not isinstance(e, TimeoutError):
                    logger.error(f"Error processing event: {e}")
                time.sleep(0.1)

# Event types
class EventTypes:
    # User events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    
    # Product events
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_DELETED = "product.deleted"
    PRODUCT_LOW_STOCK = "product.low_stock"
    PRODUCT_OUT_OF_STOCK = "product.out_of_stock"
    
    # Sale events
    SALE_CREATED = "sale.created"
    SALE_UPDATED = "sale.updated"
    SALE_DELETED = "sale.deleted"
    SALE_COMPLETED = "sale.completed"
    SALE_CANCELLED = "sale.cancelled"
    
    # Inventory events
    INVENTORY_UPDATED = "inventory.updated"
    INVENTORY_LOW = "inventory.low"
    INVENTORY_CRITICAL = "inventory.critical"
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    SYSTEM_BACKUP = "system.backup"
    SYSTEM_RESTORE = "system.restore"
    
    # Notification events
    NOTIFICATION_CREATED = "notification.created"
    NOTIFICATION_READ = "notification.read"
    NOTIFICATION_DELETED = "notification.deleted"

# Example usage:
# event_system = EventSystem()
# event_system.start()
# 
# def handle_user_login(data):
#     print(f"User logged in: {data}")
# 
# event_system.subscribe(EventTypes.USER_LOGIN, handle_user_login)
# event_system.publish(EventTypes.USER_LOGIN, {"username": "john"}) 
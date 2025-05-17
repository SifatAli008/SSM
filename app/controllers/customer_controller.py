from app.models.customers import CustomersModel
from app.utils.event_system import global_event_system

class CustomerController:
    def __init__(self, db_conn):
        self.model = CustomersModel(db_conn)

    def add_customer(self, **kwargs):
        result = self.model.add_customer(**kwargs)
        # Notify the event system about the new customer
        if result:
            global_event_system.notify_customer_update()
        return result

    def get_customers(self, search=None):
        return self.model.get_customers(search)

    def update_customer(self, customer_id, **kwargs):
        result = self.model.update_customer(customer_id, **kwargs)
        # Notify the event system about the customer update
        if result:
            global_event_system.notify_customer_update()
        return result

    def delete_customer(self, customer_id):
        result = self.model.delete_customer(customer_id)
        # Notify the event system about the customer deletion
        if result:
            global_event_system.notify_customer_update()
        return result

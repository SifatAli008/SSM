from models.customers import CustomersModel

class CustomerController:
    def __init__(self, db_conn):
        self.model = CustomersModel(db_conn)

    def add_customer(self, **kwargs):
        return self.model.add_customer(**kwargs)

    def get_customers(self, search=None):
        return self.model.get_customers(search)

    def update_customer(self, customer_id, **kwargs):
        return self.model.update_customer(customer_id, **kwargs)

    def delete_customer(self, customer_id):
        return self.model.delete_customer(customer_id)

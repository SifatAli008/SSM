from app.models.purchases import PurchasesModel

class PurchasesController:
    def __init__(self, db_conn):
        self.model = PurchasesModel(db_conn)

    def add_purchase(self, customer_id, product, quantity, price, total, date):
        return self.model.add_purchase(customer_id, product, quantity, price, total, date)

    def get_all_purchases(self):
        return self.model.get_all_purchases()

    def get_purchases_by_customer(self, customer_id):
        return self.model.get_purchases_by_customer(customer_id) 
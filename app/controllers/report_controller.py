__all__ = ['ReportController']

class ReportController:
    def __init__(self, db=None):
        self.db = db
    def generate_inventory_report(self, *args, **kwargs):
        return {}
    def generate_sales_report(self, *args, **kwargs):
        return {}

ReportController = ReportController
globals()['ReportController'] = ReportController 
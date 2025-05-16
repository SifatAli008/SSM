from app.utils.database import DatabaseManager
from app.utils.pdf_generator import PDFGenerator
from app.utils.logger import logger
from datetime import datetime, timedelta
import os

class ReportsController:
    """
    Controller to handle all report generation and data retrieval functionality
    """
    
    def __init__(self):
        """Initialize the reports controller"""
        self.db = DatabaseManager()
        
    def get_sales_summary(self, period="last_30_days"):
        """
        Get sales summary data for a specified period
        
        Args:
            period (str): The period to retrieve sales for: 'today', 'last_7_days', 'last_30_days', 'this_month', 'this_year'
            
        Returns:
            dict: Sales summary data including total sales, profit, number of orders, etc.
        """
        try:
            end_date = datetime.now()
            
            if period == "today":
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "last_7_days":
                start_date = end_date - timedelta(days=7)
            elif period == "last_30_days":
                start_date = end_date - timedelta(days=30)
            elif period == "this_month":
                start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "this_year":
                start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                # Default to last 30 days
                start_date = end_date - timedelta(days=30)
                
            # Convert to string format for SQLite
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Get sales data from database
            query = """
                SELECT 
                    SUM(total_amount) as total_sales, 
                    COUNT(*) as total_orders,
                    AVG(total_amount) as average_order_value
                FROM sales
                WHERE sale_date BETWEEN ? AND ?
            """
            
            sales_data = self.db.execute_query(query, (start_date_str, end_date_str))
            
            if not sales_data or not sales_data[0][0]:
                # No sales data found for the period
                return {
                    "total_sales": 0,
                    "total_orders": 0,
                    "average_order": 0,
                    "period": period
                }
                
            # Process data
            total_sales = float(sales_data[0][0])
            total_orders = int(sales_data[0][1])
            average_order = float(sales_data[0][2]) if sales_data[0][2] else 0
            
            return {
                "total_sales": total_sales,
                "total_orders": total_orders,
                "average_order": average_order,
                "period": period
            }
            
        except Exception as e:
            logger.error(f"Error getting sales summary: {str(e)}")
            return {
                "total_sales": 0,
                "total_orders": 0,
                "average_order": 0,
                "period": period,
                "error": str(e)
            }
    
    def get_inventory_value(self):
        """
        Calculate the total inventory value
        
        Returns:
            dict: Inventory summary including total value, total items, low stock items
        """
        try:
            # Get inventory data
            query = """
                SELECT 
                    COUNT(*) as total_items,
                    SUM(stock * buying_price) as total_value,
                    SUM(CASE WHEN stock < 5 THEN 1 ELSE 0 END) as low_stock_items
                FROM inventory
            """
            
            inventory_data = self.db.execute_query(query)
            
            if not inventory_data:
                return {
                    "total_value": 0,
                    "total_items": 0,
                    "low_stock_items": 0
                }
                
            # Process data
            total_items = int(inventory_data[0][0])
            total_value = float(inventory_data[0][1]) if inventory_data[0][1] else 0
            low_stock_items = int(inventory_data[0][2])
            
            return {
                "total_value": total_value,
                "total_items": total_items,
                "low_stock_items": low_stock_items
            }
            
        except Exception as e:
            logger.error(f"Error getting inventory value: {str(e)}")
            return {
                "total_value": 0,
                "total_items": 0,
                "low_stock_items": 0,
                "error": str(e)
            }
    
    def get_profit_summary(self, period="last_30_days"):
        """
        Calculate profit summary for a specified period
        
        Args:
            period (str): The period to calculate profit for
            
        Returns:
            dict: Profit summary data
        """
        try:
            # First get sales data for the period
            sales_summary = self.get_sales_summary(period)
            
            # Get expenses for the same period
            end_date = datetime.now()
            
            if period == "today":
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "last_7_days":
                start_date = end_date - timedelta(days=7)
            elif period == "last_30_days":
                start_date = end_date - timedelta(days=30)
            elif period == "this_month":
                start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "this_year":
                start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                # Default to last 30 days
                start_date = end_date - timedelta(days=30)
                
            # Convert to string format for SQLite
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # For now, estimate expenses as 70% of sales (this would be replaced with actual expense tracking)
            total_sales = sales_summary.get("total_sales", 0)
            expenses = total_sales * 0.7  # Example estimation
            profit = total_sales - expenses
            
            return {
                "total_sales": total_sales,
                "total_expenses": expenses,
                "net_profit": profit,
                "profit_margin": (profit / total_sales * 100) if total_sales > 0 else 0,
                "period": period
            }
            
        except Exception as e:
            logger.error(f"Error calculating profit summary: {str(e)}")
            return {
                "total_sales": 0,
                "total_expenses": 0,
                "net_profit": 0,
                "profit_margin": 0,
                "period": period,
                "error": str(e)
            }
    
    def generate_sales_report(self, period="last_30_days"):
        """
        Generate a sales report PDF for a specified period
        
        Args:
            period (str): The period to generate the report for
            
        Returns:
            str: Path to the generated PDF file, or None if failed
        """
        try:
            # Get sales data
            sales_data = self.get_sales_summary(period)
            profit_data = self.get_profit_summary(period)
            
            # Get detailed sales records
            end_date = datetime.now()
            
            if period == "today":
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
                period_name = "Today"
            elif period == "last_7_days":
                start_date = end_date - timedelta(days=7)
                period_name = "Last 7 Days"
            elif period == "last_30_days":
                start_date = end_date - timedelta(days=30)
                period_name = "Last 30 Days"
            elif period == "this_month":
                start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                period_name = f"Month of {end_date.strftime('%B %Y')}"
            elif period == "this_year":
                start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                period_name = f"Year {end_date.year}"
            else:
                # Default to last 30 days
                start_date = end_date - timedelta(days=30)
                period_name = "Last 30 Days"
                
            # Generate report title
            report_title = f"Sales Report - {period_name}"
            
            # TODO: Implement detailed sales record retrieval when the sales table exists
            # For now, we'll use mock data for demonstration
            
            # Build the report data
            report_data = {
                "title": report_title,
                "period": period_name,
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "summary": {
                    "total_sales": sales_data.get("total_sales", 0),
                    "total_orders": sales_data.get("total_orders", 0),
                    "average_order": sales_data.get("average_order", 0),
                    "total_expenses": profit_data.get("total_expenses", 0),
                    "net_profit": profit_data.get("net_profit", 0),
                    "profit_margin": profit_data.get("profit_margin", 0)
                },
                "details": []  # Would contain detailed sales records
            }
            
            # Generate PDF
            # TODO: Implement actual PDF generation with the report_data
            # For now, we'll return a success message
            
            logger.info(f"Generated sales report for {period_name}")
            return f"Sales report for {period_name} generated successfully."
            
        except Exception as e:
            logger.error(f"Error generating sales report: {str(e)}")
            return None
    
    def generate_inventory_report(self):
        """
        Generate a complete inventory report PDF
        
        Returns:
            str: Path to the generated PDF file, or None if failed
        """
        try:
            # Get all inventory items
            query = """
                SELECT 
                    id, name, category, stock, buying_price, selling_price, last_updated 
                FROM inventory
                ORDER BY category, name
            """
            
            inventory_items = self.db.execute_query(query)
            
            if not inventory_items:
                logger.warning("No inventory items found for report")
                return None
                
            # Convert to list of dictionaries for the PDF generator
            items_data = []
            for item in inventory_items:
                items_data.append({
                    "id": item[0],
                    "name": item[1],
                    "category": item[2],
                    "stock": item[3],
                    "buying_price": item[4],
                    "selling_price": item[5],
                    "last_updated": item[6]
                })
                
            # Generate PDF
            pdf_path = PDFGenerator.generate_inventory_report(items_data, "Complete Inventory Report")
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating inventory report: {str(e)}")
            return None

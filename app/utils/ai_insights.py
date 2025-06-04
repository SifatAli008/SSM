import numpy as np
from datetime import datetime, timedelta
from app.utils.logger import Logger

logger = Logger()

class AIInsights:
    """
    A utility class that provides AI-like insights without requiring complex ML libraries.
    This is a simplified version that can be enhanced with actual ML models in the future.
    """
    
    @staticmethod
    def analyze_sales_trend(sales_data, period_days=30):
        """
        Analyze sales data to identify trends
        
        Args:
            sales_data: List of (date, amount) tuples
            period_days: Number of days to analyze
            
        Returns:
            dict: Analysis results
        """
        try:
            if not sales_data:
                return {
                    "trend": "neutral",
                    "growth_rate": 0,
                    "insight": "Insufficient data for trend analysis"
                }
                
            # Convert data to numpy arrays for analysis
            dates = [datetime.strptime(date_str, "%Y-%m-%d") 
                    if isinstance(date_str, str) else date_str 
                    for date_str, _ in sales_data]
            amounts = [float(amount) for _, amount in sales_data]
            
            # Check if we have enough data
            if len(dates) < 2:
                return {
                    "trend": "neutral",
                    "growth_rate": 0,
                    "insight": "More data needed for trend analysis"
                }
                
            # Sort by date
            indices = np.argsort(dates)
            dates = [dates[i] for i in indices]
            amounts = [amounts[i] for i in indices]
            
            # Split into two periods for comparison
            midpoint = len(dates) // 2
            
            if midpoint == 0:
                return {
                    "trend": "neutral",
                    "growth_rate": 0,
                    "insight": "More data needed for trend analysis"
                }
                
            first_period_avg = sum(amounts[:midpoint]) / midpoint
            second_period_avg = sum(amounts[midpoint:]) / (len(amounts) - midpoint)
            
            # Calculate growth rate
            if first_period_avg == 0:
                growth_rate = 0
            else:
                growth_rate = ((second_period_avg - first_period_avg) / first_period_avg) * 100
            
            # Determine trend
            if growth_rate > 5:
                trend = "positive"
                insight = f"Sales are increasing by {growth_rate:.1f}% between periods"
            elif growth_rate < -5:
                trend = "negative"
                insight = f"Sales are decreasing by {abs(growth_rate):.1f}% between periods"
            else:
                trend = "neutral"
                insight = "Sales are relatively stable between periods"
                
            return {
                "trend": trend,
                "growth_rate": growth_rate,
                "insight": insight
            }
            
        except Exception as e:
            logger.error(f"Error in sales trend analysis: {str(e)}")
            return {
                "trend": "error",
                "growth_rate": 0,
                "insight": f"Error analyzing sales trend: {str(e)}"
            }
    
    @staticmethod
    def identify_top_products(sales_data, limit=5):
        """
        Identify top-selling products from sales data
        
        Args:
            sales_data: List of (product_id, product_name, quantity, amount) tuples
            limit: Number of top products to return
            
        Returns:
            list: Top products with stats
        """
        try:
            if not sales_data:
                return []
                
            # Group by product and sum quantities
            product_sales = {}
            
            for product_id, product_name, quantity, amount in sales_data:
                if product_id not in product_sales:
                    product_sales[product_id] = {
                        "product_id": product_id,
                        "product_name": product_name,
                        "total_quantity": 0,
                        "total_amount": 0
                    }
                
                product_sales[product_id]["total_quantity"] += quantity
                product_sales[product_id]["total_amount"] += amount
            
            # Convert to list and sort by total amount
            products_list = list(product_sales.values())
            products_list.sort(key=lambda x: x["total_amount"], reverse=True)
            
            # Return top products
            top_products = products_list[:limit]
            
            return top_products
            
        except Exception as e:
            logger.error(f"Error identifying top products: {str(e)}")
            return []
    
    @staticmethod
    def predict_stock_needs(inventory_data, sales_velocity_data, days_forecast=30):
        """
        Predict stock needs based on inventory and sales velocity
        
        Args:
            inventory_data: List of (product_id, product_name, current_stock) tuples
            sales_velocity_data: List of (product_id, units_per_day) tuples
            days_forecast: Number of days to forecast
            
        Returns:
            list: Products that need reordering with quantities
        """
        try:
            if not inventory_data or not sales_velocity_data:
                return []
                
            # Convert sales velocity to dictionary for easier lookup
            velocity_dict = {product_id: units_per_day for product_id, units_per_day in sales_velocity_data}
            
            # Analyze each inventory item
            restock_needs = []
            
            for product_id, product_name, current_stock in inventory_data:
                # Skip if no sales velocity data
                if product_id not in velocity_dict:
                    continue
                    
                velocity = velocity_dict[product_id]
                
                # Calculate days of inventory left
                if velocity > 0:
                    days_left = current_stock / velocity
                else:
                    days_left = float('inf')  # Infinite if no sales
                
                # Calculate needed stock for forecast period
                needed_for_period = velocity * days_forecast
                
                # Determine if reordering is needed
                if days_left < days_forecast:
                    reorder_quantity = int(needed_for_period - current_stock)
                    
                    if reorder_quantity > 0:
                        restock_needs.append({
                            "product_id": product_id,
                            "product_name": product_name,
                            "current_stock": current_stock,
                            "days_remaining": days_left,
                            "reorder_quantity": reorder_quantity
                        })
            
            # Sort by days remaining (ascending)
            restock_needs.sort(key=lambda x: x["days_remaining"])
            
            return restock_needs
            
        except Exception as e:
            logger.error(f"Error predicting stock needs: {str(e)}")
            return []
    
    @staticmethod
    def generate_business_insight(sales_data, inventory_data, expenses_data=None):
        """
        Generate a high-level business insight based on available data
        
        Args:
            sales_data: Sales summary data dictionary
            inventory_data: Inventory summary data dictionary
            expenses_data: Optional expenses data dictionary
            
        Returns:
            str: Business insight text
        """
        try:
            # Start with a general insight
            insights = []
            
            # Sales insights
            if sales_data:
                total_sales = sales_data.get('total_sales', 0)
                total_orders = sales_data.get('total_orders', 0)
                
                if total_sales > 0:
                    insights.append(f"Total sales of ${total_sales:,.2f} from {total_orders:,} orders.")
                    
                    # Add trend if available
                    if 'trend' in sales_data:
                        trend = sales_data['trend']
                        growth_rate = sales_data.get('growth_rate', 0)
                        
                        if trend == 'positive':
                            insights.append(f"Sales are trending upward by {growth_rate:.1f}%.")
                        elif trend == 'negative':
                            insights.append(f"Sales are trending downward by {abs(growth_rate):.1f}%.")
            
            # Inventory insights
            if inventory_data:
                total_items = inventory_data.get('total_items', 0)
                total_value = inventory_data.get('total_value', 0)
                low_stock_items = inventory_data.get('low_stock_items', 0)
                
                insights.append(f"Inventory consists of {total_items:,} items valued at ${total_value:,.2f}.")
                
                if low_stock_items > 0:
                    insights.append(f"Alert: {low_stock_items:,} items need restocking soon.")
            
            # Profit/margin insights
            if sales_data and expenses_data:
                total_sales = sales_data.get('total_sales', 0)
                total_expenses = expenses_data.get('total_expenses', 0)
                
                if total_sales > 0 and total_expenses > 0:
                    profit = total_sales - total_expenses
                    profit_margin = (profit / total_sales) * 100 if total_sales > 0 else 0
                    
                    insights.append(f"Net profit is ${profit:,.2f} with a margin of {profit_margin:.1f}%.")
                    
                    if profit_margin < 10:
                        insights.append("Consider strategies to improve profit margins.")
                    elif profit_margin > 30:
                        insights.append("Strong profit margins suggest healthy business operations.")
            
            # Join insights with spaces
            if insights:
                return " ".join(insights)
            else:
                return "Insufficient data to generate business insights."
            
        except Exception as e:
            logger.error(f"Error generating business insight: {str(e)}")
            return "Error generating business insights."

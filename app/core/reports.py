import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.utils.logger import logger
from app.utils.config_manager import config_manager
from app.utils.database import db_manager
from app.core.event_system import EventSystem, EventTypes

class ReportManager:
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self._setup_report_directory()
    
    def _setup_report_directory(self):
        """Set up report directory if it doesn't exist."""
        report_dir = Path(config_manager.get('app.report_output_path'))
        report_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Report directory set up: {report_dir}")
    
    def generate_sales_report(self, start_date: datetime, end_date: datetime, format: str = 'pdf') -> Optional[str]:
        """Generate sales report for a date range."""
        try:
            with db_manager.get_session() as session:
                # Query sales data
                sales_data = session.execute("""
                    SELECT 
                        s.id,
                        s.created_at,
                        u.username,
                        s.total_amount,
                        s.payment_method,
                        s.status,
                        COUNT(si.id) as items_count
                    FROM sales s
                    JOIN users u ON s.user_id = u.id
                    JOIN sale_items si ON s.id = si.sale_id
                    WHERE s.created_at BETWEEN :start_date AND :end_date
                    GROUP BY s.id
                    ORDER BY s.created_at DESC
                """, {
                    'start_date': start_date,
                    'end_date': end_date
                }).fetchall()
                
                if not sales_data:
                    logger.warning("No sales data found for the specified date range")
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(sales_data, columns=[
                    'ID', 'Date', 'User', 'Amount', 'Payment Method',
                    'Status', 'Items Count'
                ])
                
                # Generate report
                report_file = self._generate_report(
                    df,
                    'sales_report',
                    start_date,
                    end_date,
                    format
                )
                
                # Publish event
                self.event_system.publish(EventTypes.SYSTEM_REPORT_GENERATED, {
                    'report_type': 'sales',
                    'report_file': report_file,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                })
                
                return report_file
        except Exception as e:
            logger.error(f"Failed to generate sales report: {e}")
            return None
    
    def generate_inventory_report(self, format: str = 'pdf') -> Optional[str]:
        """Generate inventory status report."""
        try:
            with db_manager.get_session() as session:
                # Query inventory data
                inventory_data = session.execute("""
                    SELECT 
                        p.id,
                        p.name,
                        p.category,
                        p.sku,
                        p.stock,
                        p.min_stock,
                        p.price,
                        p.cost
                    FROM products p
                    ORDER BY p.category, p.name
                """).fetchall()
                
                if not inventory_data:
                    logger.warning("No inventory data found")
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(inventory_data, columns=[
                    'ID', 'Name', 'Category', 'SKU', 'Stock',
                    'Min Stock', 'Price', 'Cost'
                ])
                
                # Generate report
                report_file = self._generate_report(
                    df,
                    'inventory_report',
                    datetime.now(),
                    datetime.now(),
                    format
                )
                
                # Publish event
                self.event_system.publish(EventTypes.SYSTEM_REPORT_GENERATED, {
                    'report_type': 'inventory',
                    'report_file': report_file
                })
                
                return report_file
        except Exception as e:
            logger.error(f"Failed to generate inventory report: {e}")
            return None
    
    def _generate_report(self, df: pd.DataFrame, report_type: str, start_date: datetime, end_date: datetime, format: str) -> str:
        """Generate report in specified format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Path(config_manager.get('app.report_output_path'))
        
        if format == 'pdf':
            report_file = report_dir / f"{report_type}_{timestamp}.pdf"
            self._generate_pdf_report(df, report_file, report_type, start_date, end_date)
        elif format == 'csv':
            report_file = report_dir / f"{report_type}_{timestamp}.csv"
            df.to_csv(report_file, index=False)
        elif format == 'excel':
            report_file = report_dir / f"{report_type}_{timestamp}.xlsx"
            df.to_excel(report_file, index=False)
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        logger.info(f"Report generated: {report_file}")
        return str(report_file)
    
    def _generate_pdf_report(self, df: pd.DataFrame, output_file: Path, report_type: str, start_date: datetime, end_date: datetime):
        """Generate PDF report."""
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Add title
        title = Paragraph(f"{report_type.replace('_', ' ').title()} Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Add date range
        date_range = Paragraph(
            f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            styles['Normal']
        )
        elements.append(date_range)
        elements.append(Spacer(1, 12))
        
        # Add summary statistics
        if report_type == 'sales_report':
            total_sales = df['Amount'].sum()
            avg_sale = df['Amount'].mean()
            total_items = df['Items Count'].sum()
            
            summary = [
                f"Total Sales: ${total_sales:.2f}",
                f"Average Sale: ${avg_sale:.2f}",
                f"Total Items Sold: {total_items}"
            ]
            
            for stat in summary:
                elements.append(Paragraph(stat, styles['Normal']))
            elements.append(Spacer(1, 12))
        
        # Add data table
        data = [df.columns.tolist()] + df.values.tolist()
        table = Table(data)
        
        # Add table style
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
    
    def list_reports(self) -> List[dict]:
        """List all available reports."""
        try:
            report_dir = Path(config_manager.get('app.report_output_path'))
            reports = []
            
            for report_file in report_dir.glob("*.*"):
                if report_file.suffix in ['.pdf', '.csv', '.xlsx']:
                    stat = report_file.stat()
                    reports.append({
                        'filename': report_file.name,
                        'path': str(report_file),
                        'type': report_file.suffix[1:],
                        'size': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            return sorted(reports, key=lambda x: x['created_at'], reverse=True)
        except Exception as e:
            logger.error(f"Failed to list reports: {e}")
            return []
    
    def delete_report(self, report_file: str) -> bool:
        """Delete a report file."""
        try:
            report_path = Path(report_file)
            if report_path.exists():
                report_path.unlink()
                logger.info(f"Report deleted: {report_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete report: {e}")
            return False 
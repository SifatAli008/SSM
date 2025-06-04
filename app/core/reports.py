import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.utils.logger import Logger
from app.utils.config_manager import config_manager
from app.utils.database import db_manager
from app.core.event_system import EventSystem, EventTypes
from app.ui.firebase_utils import get_db

logger = Logger()

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
        """Generate sales report for a date range from Firebase."""
        try:
            sales_data_obj = get_db().child('sales').get()
            sales_data = sales_data_obj.val() if hasattr(sales_data_obj, 'val') else sales_data_obj or {}
            sales = []
            for v in sales_data.values():
                sale_date = pd.to_datetime(v.get('sale_date'))
                if start_date <= sale_date <= end_date:
                    sales.append(v)
            if not sales:
                logger.warning("No sales data found for the specified date range")
                return None
            df = pd.DataFrame(sales)
            report_file = self._generate_report(df, 'sales_report', start_date, end_date, format)
            return report_file
        except Exception as e:
            logger.error(f"Failed to generate sales report: {e}")
            return None
    
    def generate_inventory_report(self, format: str = 'pdf') -> Optional[str]:
        """Generate inventory status report from Firebase."""
        try:
            inventory_data_obj = get_db().child('inventory').get()
            inventory_data = inventory_data_obj.val() if hasattr(inventory_data_obj, 'val') else inventory_data_obj or {}
            inventory = list(inventory_data.values())
            if not inventory:
                logger.warning("No inventory data found")
                return None
            df = pd.DataFrame(inventory)
            now = datetime.now()
            report_file = self._generate_report(df, 'inventory_report', now, now, format)
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
        
        # Add data table
        if not df.empty:
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
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.units import inch, cm
import os
from pathlib import Path
from datetime import datetime
from app.utils.logger import logger


class PDFGenerator:
    """
    Utility class to generate PDF reports and invoices
    """
    
    @staticmethod
    def get_reports_dir():
        """Return the path to the reports directory"""
        base_dir = Path(__file__).resolve().parent.parent.parent
        reports_dir = os.path.join(base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        return reports_dir
    
    @staticmethod
    def generate_invoice(order_data, customer_data, items_data):
        """
        Generate a customer invoice PDF
        
        Args:
            order_data: Dictionary with order information (order_id, date, total, etc.)
            customer_data: Dictionary with customer information (name, address, etc.)
            items_data: List of dictionaries with item information (name, quantity, price, etc.)
        
        Returns:
            str: Path to the generated PDF file
        """
        try:
            # Create the file path
            reports_dir = PDFGenerator.get_reports_dir()
            today = datetime.now().strftime("%Y%m%d")
            filename = f"invoice_{order_data.get('order_id', 'unknown')}_{today}.pdf"
            filepath = os.path.join(reports_dir, filename)
            
            # Create the document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Collect all the elements
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            subtitle_style = styles['Heading2']
            normal_style = styles['Normal']
            
            # Add invoice title
            elements.append(Paragraph(f"INVOICE #{order_data.get('order_id', '')}", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Add date
            elements.append(Paragraph(f"Date: {order_data.get('date', datetime.now().strftime('%Y-%m-%d'))}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add customer information
            elements.append(Paragraph("Bill To:", subtitle_style))
            elements.append(Paragraph(f"Name: {customer_data.get('name', '')}", normal_style))
            elements.append(Paragraph(f"Address: {customer_data.get('address', '')}", normal_style))
            elements.append(Paragraph(f"Phone: {customer_data.get('phone', '')}", normal_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Create table for items
            table_data = [["Item", "Quantity", "Unit Price", "Total"]]
            
            # Add items to table
            for item in items_data:
                table_data.append([
                    item.get('name', ''),
                    item.get('quantity', ''),
                    f"${item.get('unit_price', 0):.2f}",
                    f"${item.get('total', 0):.2f}"
                ])
                
            # Calculate subtotal, tax, and total
            subtotal = sum(item.get('total', 0) for item in items_data)
            tax_rate = order_data.get('tax_rate', 0.1)  # Default 10% tax
            tax = subtotal * tax_rate
            total = subtotal + tax
            
            # Add summary rows
            table_data.append(["", "", "Subtotal", f"${subtotal:.2f}"])
            table_data.append(["", "", f"Tax ({tax_rate*100:.0f}%)", f"${tax:.2f}"])
            table_data.append(["", "", "Total", f"${total:.2f}"])
            
            # Create the table
            table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
            
            # Style the table
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
                ('BACKGROUND', (2, -3), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (2, -3), (-1, -1), 'Helvetica-Bold'),
            ])
            table.setStyle(table_style)
            
            elements.append(table)
            elements.append(Spacer(1, 0.5*inch))
            
            # Add payment terms and thank you note
            elements.append(Paragraph("Payment Terms: Due on receipt", normal_style))
            elements.append(Spacer(1, 0.25*inch))
            elements.append(Paragraph("Thank you for your business!", subtitle_style))
            
            # Build the PDF
            doc.build(elements)
            
            logger.info(f"Invoice generated successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating invoice: {str(e)}")
            return None
    
    @staticmethod
    def generate_inventory_report(inventory_data, report_title="Inventory Report"):
        """
        Generate an inventory report PDF
        
        Args:
            inventory_data: List of dictionaries with inventory item information
            report_title: Title of the report
        
        Returns:
            str: Path to the generated PDF file
        """
        try:
            # Create the file path
            reports_dir = PDFGenerator.get_reports_dir()
            today = datetime.now().strftime("%Y%m%d")
            filename = f"inventory_report_{today}.pdf"
            filepath = os.path.join(reports_dir, filename)
            
            # Create the document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Collect all the elements
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            normal_style = styles['Normal']
            
            # Add title and date
            elements.append(Paragraph(report_title, title_style))
            elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Create table for inventory items
            table_data = [["ID", "Product Name", "Category", "Stock", "Buying Price", "Selling Price"]]
            
            # Add items to table
            for item in inventory_data:
                table_data.append([
                    str(item.get('id', '')),
                    item.get('name', ''),
                    item.get('category', ''),
                    str(item.get('stock', 0)),
                    f"${item.get('buying_price', 0):.2f}",
                    f"${item.get('selling_price', 0):.2f}"
                ])
                
            # Create the table
            table = Table(table_data)
            
            # Style the table
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (3, 1), (5, -1), 'RIGHT'),
            ])
            table.setStyle(table_style)
            
            elements.append(table)
            
            # Build the PDF
            doc.build(elements)
            
            logger.info(f"Inventory report generated successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating inventory report: {str(e)}")
            return None

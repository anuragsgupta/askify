"""
Script to create demo data for SME Knowledge Agent.

Creates:
- 2-3 policy PDFs with version conflicts
- 1-2 pricing Excel files with client data
- 2-3 EML files with email threads
"""

import os
from datetime import datetime
from pathlib import Path

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER

# Excel generation
from openpyxl import Workbook

# Email generation
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate


def create_pdf_with_toc(filename, title, date_str, sections):
    """
    Create a PDF with table of contents and sections.
    
    Args:
        filename: Output filename
        title: Document title
        date_str: Date string to include in document
        sections: List of (section_title, section_number, content) tuples
    """
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Add title page
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Effective Date: {date_str}", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Add table of contents
    story.append(Paragraph("Table of Contents", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))
    
    for section_title, section_number, _ in sections:
        toc_entry = f"{section_number}. {section_title}"
        story.append(Paragraph(toc_entry, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Add sections
    for section_title, section_number, content in sections:
        # Section heading
        heading = f"{section_number}. {section_title}"
        story.append(Paragraph(heading, styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Section content
        for paragraph in content.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.3*inch))
    
    doc.build(story)


def create_demo_pdfs():
    """Create demo policy PDFs with version conflicts."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # PDF 1: Refund Policy v1 (older version)
    sections_v1 = [
        ("Refund Eligibility", "1", 
         "Customers may request a refund within 30 days of purchase.\n\n"
         "To be eligible for a refund, the product must be unused and in its original packaging.\n\n"
         "Digital products are non-refundable unless they are defective."),
        
        ("Refund Process", "2",
         "To initiate a refund, customers must contact our support team at support@company.com.\n\n"
         "Refunds will be processed within 5-7 business days after approval.\n\n"
         "The refund will be issued to the original payment method."),
        
        ("Exceptions", "3",
         "Sale items and clearance products are final sale and cannot be refunded.\n\n"
         "Shipping costs are non-refundable unless the product was damaged or defective.")
    ]
    
    create_pdf_with_toc(
        "data/Refund_Policy_v1_January2023.pdf",
        "Refund Policy - Version 1",
        "January 15, 2023",
        sections_v1
    )
    
    # PDF 2: Refund Policy v2 (newer version with conflicts)
    sections_v2 = [
        ("Refund Eligibility", "1",
         "Customers may request a refund within 60 days of purchase.\n\n"  # Changed from 30 to 60 days
         "To be eligible for a refund, the product must be unused and in its original packaging.\n\n"
         "Digital products can be refunded within 14 days if they are defective or not as described."),  # Changed policy
        
        ("Refund Process", "2",
         "To initiate a refund, customers must contact our support team at support@company.com or use our online refund portal.\n\n"  # Added online portal
         "Refunds will be processed within 3-5 business days after approval.\n\n"  # Changed from 5-7 to 3-5 days
         "The refund will be issued to the original payment method."),
        
        ("Exceptions", "3",
         "Sale items can be refunded within 30 days with a 20% restocking fee.\n\n"  # Changed from final sale
         "Shipping costs are refundable if the product was damaged, defective, or if we made an error.")  # Expanded policy
    ]
    
    create_pdf_with_toc(
        "data/Refund_Policy_v2_March2024.pdf",
        "Refund Policy - Version 2",
        "March 1, 2024",
        sections_v2
    )
    
    # PDF 3: Shipping Policy
    sections_shipping = [
        ("Domestic Shipping", "1",
         "Standard shipping takes 5-7 business days and costs $5.99.\n\n"
         "Express shipping takes 2-3 business days and costs $15.99.\n\n"
         "Free shipping is available on orders over $50."),
        
        ("International Shipping", "2",
         "International shipping is available to select countries.\n\n"
         "Delivery times vary by destination, typically 10-21 business days.\n\n"
         "International shipping costs are calculated at checkout based on weight and destination.\n\n"
         "Customers are responsible for any customs duties or import taxes."),
        
        ("Tracking", "3",
         "All orders include tracking information sent via email.\n\n"
         "Tracking numbers are provided within 24 hours of shipment.\n\n"
         "Customers can track their orders on our website or the carrier's website.")
    ]
    
    create_pdf_with_toc(
        "data/Shipping_Policy_February2024.pdf",
        "Shipping Policy",
        "February 10, 2024",
        sections_shipping
    )
    
    print("✓ Created 3 policy PDFs with version conflicts")


def create_demo_excel_files():
    """Create demo pricing Excel files with client data."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Excel 1: Q1 2024 Pricing
    wb1 = Workbook()
    ws1 = wb1.active
    ws1.title = "Q1_Pricing"
    
    # Headers
    ws1.append(["Client", "Product", "Price", "Discount", "Final Price", "Date"])
    
    # Data rows with formulas
    data_q1 = [
        ["Acme Corp", "Widget Pro", 500, 0.10, "=C2*(1-D2)", "2024-01-15"],
        ["TechStart Inc", "Widget Basic", 300, 0.05, "=C3*(1-D3)", "2024-01-20"],
        ["Global Solutions", "Widget Enterprise", 1200, 0.15, "=C4*(1-D4)", "2024-02-01"],
        ["Acme Corp", "Widget Basic", 300, 0.10, "=C5*(1-D5)", "2024-02-15"],
        ["InnovateCo", "Widget Pro", 500, 0.08, "=C6*(1-D6)", "2024-03-01"],
        ["TechStart Inc", "Widget Enterprise", 1200, 0.05, "=C7*(1-D7)", "2024-03-10"],
    ]
    
    for row in data_q1:
        ws1.append(row)
    
    wb1.save("data/Pricing_Q1_2024.xlsx")
    
    # Excel 2: Q2 2024 Pricing (with price changes)
    wb2 = Workbook()
    ws2 = wb2.active
    ws2.title = "Q2_Pricing"
    
    # Headers
    ws2.append(["Client", "Product", "Price", "Discount", "Final Price", "Date"])
    
    # Data rows with updated prices
    data_q2 = [
        ["Acme Corp", "Widget Pro", 550, 0.10, "=C2*(1-D2)", "2024-04-01"],  # Price increased
        ["TechStart Inc", "Widget Basic", 280, 0.05, "=C3*(1-D3)", "2024-04-15"],  # Price decreased
        ["Global Solutions", "Widget Enterprise", 1300, 0.15, "=C4*(1-D4)", "2024-05-01"],  # Price increased
        ["NewClient LLC", "Widget Pro", 550, 0.12, "=C5*(1-D5)", "2024-05-15"],  # New client
        ["InnovateCo", "Widget Enterprise", 1300, 0.10, "=C6*(1-D6)", "2024-06-01"],
        ["Acme Corp", "Widget Enterprise", 1300, 0.15, "=C7*(1-D7)", "2024-06-15"],
    ]
    
    for row in data_q2:
        ws2.append(row)
    
    wb2.save("data/Pricing_Q2_2024.xlsx")
    
    print("✓ Created 2 pricing Excel files with client data")


def create_demo_email_files():
    """Create demo EML files with email threads."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Email 1: Customer inquiry about refund policy (old policy)
    msg1 = MIMEMultipart()
    msg1['From'] = 'john.smith@acmecorp.com'
    msg1['To'] = 'support@company.com'
    msg1['Subject'] = 'Question about refund policy for Acme Corp'
    msg1['Date'] = formatdate(localtime=True, usegmt=False)
    msg1['Message-ID'] = '<refund-inquiry-001@acmecorp.com>'
    
    body1 = """Hi Support Team,

I'm reaching out on behalf of Acme Corp regarding your refund policy. We purchased several Widget Pro units last month and may need to return some of them.

Can you confirm the refund window? I believe it's 30 days from purchase, correct?

Also, what's the typical processing time for refunds?

Thanks,
John Smith
Procurement Manager
Acme Corp
john.smith@acmecorp.com
"""
    
    msg1.attach(MIMEText(body1, 'plain'))
    
    with open("data/Refund_Inquiry_AcmeCorp_Jan2023.eml", 'wb') as f:
        f.write(msg1.as_bytes())
    
    # Email 2: Support response (referencing old 30-day policy)
    msg2 = MIMEMultipart()
    msg2['From'] = 'support@company.com'
    msg2['To'] = 'john.smith@acmecorp.com'
    msg2['Subject'] = 'Re: Question about refund policy for Acme Corp'
    msg2['Date'] = formatdate(localtime=True, usegmt=False)
    msg2['Message-ID'] = '<refund-response-001@company.com>'
    msg2['In-Reply-To'] = '<refund-inquiry-001@acmecorp.com>'
    msg2['References'] = '<refund-inquiry-001@acmecorp.com>'
    
    body2 = """Hi John,

Thanks for reaching out! Yes, you're correct - our refund policy allows returns within 30 days of purchase.

The products must be unused and in original packaging. Once we receive and approve the return, refunds are processed within 5-7 business days.

For Acme Corp's recent Widget Pro purchase, you're still within the refund window. Just let us know which units you'd like to return and we'll send you a return authorization.

Best regards,
Sarah Johnson
Customer Support Team
support@company.com
"""
    
    msg2.attach(MIMEText(body2, 'plain'))
    
    with open("data/Refund_Response_Support_Jan2023.eml", 'wb') as f:
        f.write(msg2.as_bytes())
    
    # Email 3: Pricing inquiry (recent)
    msg3 = MIMEMultipart()
    msg3['From'] = 'mike.chen@techstart.com'
    msg3['To'] = 'sales@company.com'
    msg3['Subject'] = 'Pricing quote for TechStart Inc - Widget Enterprise'
    msg3['Date'] = formatdate(localtime=True, usegmt=False)
    msg3['Message-ID'] = '<pricing-inquiry-001@techstart.com>'
    
    body3 = """Hello Sales Team,

TechStart Inc is interested in upgrading to Widget Enterprise for our team. We currently use Widget Basic.

Could you provide a quote for 10 Widget Enterprise licenses? We saw the Q1 pricing was $1,200 per unit with a 5% discount for existing customers.

Is that pricing still current, or have there been any changes for Q2?

Also, what's the typical delivery timeframe?

Thanks,
Mike Chen
IT Director
TechStart Inc
mike.chen@techstart.com
"""
    
    msg3.attach(MIMEText(body3, 'plain'))
    
    with open("data/Pricing_Inquiry_TechStart_March2024.eml", 'wb') as f:
        f.write(msg3.as_bytes())
    
    print("✓ Created 3 EML email files")


if __name__ == "__main__":
    print("Creating demo data for SME Knowledge Agent...\n")
    
    create_demo_pdfs()
    create_demo_excel_files()
    create_demo_email_files()
    
    print("\n✅ Demo data creation complete!")
    print("\nCreated files:")
    print("  PDFs:")
    print("    - data/Refund_Policy_v1_January2023.pdf")
    print("    - data/Refund_Policy_v2_March2024.pdf")
    print("    - data/Shipping_Policy_February2024.pdf")
    print("  Excel:")
    print("    - data/Pricing_Q1_2024.xlsx")
    print("    - data/Pricing_Q2_2024.xlsx")
    print("  Emails:")
    print("    - data/Refund_Inquiry_AcmeCorp_Jan2023.eml")
    print("    - data/Refund_Response_Support_Jan2023.eml")
    print("    - data/Pricing_Inquiry_TechStart_March2024.eml")

"""Demo script for Excel parser functionality."""

from datetime import datetime
from openpyxl import Workbook
from pathlib import Path
import tempfile

from excel_parser import extract_excel_rows, row_to_natural_language


def create_demo_excel():
    """Creates a demo Excel file with sample pricing data."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Q1_Pricing"
    
    # Add headers
    ws.append(["Client", "Product", "Price", "Date", "Quantity"])
    
    # Add sample data rows
    ws.append(["Acme Corp", "Widget Pro", 500.00, datetime(2024, 3, 15), 100])
    ws.append(["Beta Industries", "Gadget Plus", 750.50, datetime(2024, 3, 20), 50])
    ws.append(["Gamma LLC", "Tool Kit", 1200.00, datetime(2024, 3, 25), 25])
    
    # Add a second sheet
    ws2 = wb.create_sheet("Q2_Pricing")
    ws2.append(["Client", "Product", "Price", "Date"])
    ws2.append(["Delta Corp", "Super Widget", 899.99, datetime(2024, 6, 10)])
    
    # Save to temp file
    tmp_path = Path(tempfile.gettempdir()) / "Demo_Pricing_March2024.xlsx"
    wb.save(tmp_path)
    wb.close()
    
    return tmp_path


def main():
    """Demonstrates Excel parsing functionality."""
    print("=" * 70)
    print("Excel Parser Demo")
    print("=" * 70)
    
    # Create demo file
    print("\n1. Creating demo Excel file...")
    excel_path = create_demo_excel()
    print(f"   Created: {excel_path}")
    
    # Extract rows
    print("\n2. Extracting rows from Excel file...")
    rows = extract_excel_rows(str(excel_path))
    print(f"   Extracted {len(rows)} rows")
    
    # Display results
    print("\n3. Extracted Row Details:")
    print("-" * 70)
    
    for i, row in enumerate(rows, 1):
        print(f"\nRow {i}:")
        print(f"  Source: {row.source}")
        print(f"  Sheet: {row.sheet_name}")
        print(f"  Row Number: {row.row_number}")
        print(f"  Client: {row.client}")
        print(f"  Date: {row.doc_date.strftime('%Y-%m-%d')}")
        print(f"  Doc Type: {row.doc_type}")
        print(f"  Content: {row.content}")
    
    # Demonstrate natural language conversion
    print("\n" + "=" * 70)
    print("Natural Language Conversion Demo")
    print("=" * 70)
    
    sample_row = {
        "Client": "Acme Corp",
        "Product": "Widget",
        "Price": 500.00,
        "Quantity": 100,
        "Date": datetime(2024, 3, 15)
    }
    
    nl_text = row_to_natural_language(sample_row)
    print(f"\nInput: {sample_row}")
    print(f"Output: {nl_text}")
    
    # Cleanup
    print("\n" + "=" * 70)
    print(f"Demo complete! Temp file: {excel_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()

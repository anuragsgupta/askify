"""Demonstration script for PDF parser functionality."""

import tempfile
from pathlib import Path

import fitz

from pdf_parser import extract_pdf_sections, parse_date_from_filename


def create_sample_pdf():
    """Creates a sample PDF with TOC for demonstration."""
    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        prefix="Company_Policy_March2024_",
        delete=False
    ) as tmp:
        doc = fitz.open()
        
        # Create pages with content
        page1 = doc.new_page()
        page1.insert_text((72, 72), "Introduction\n\nThis is the introduction section.")
        
        page2 = doc.new_page()
        page2.insert_text((72, 72), "Refund Policy\n\nRefund window is 60 days.")
        
        page3 = doc.new_page()
        page3.insert_text((72, 72), "Exceptions\n\nSpecial cases apply.")
        
        page4 = doc.new_page()
        page4.insert_text((72, 72), "Contact Information\n\nEmail: support@company.com")
        
        # Create hierarchical TOC
        toc = [
            [1, "Introduction", 1],
            [1, "Refund Policy", 2],
            [2, "Exceptions", 3],
            [1, "Contact Information", 4],
        ]
        doc.set_toc(toc)
        
        doc.save(tmp.name)
        doc.close()
        
        return tmp.name


def main():
    """Demonstrates PDF parsing functionality."""
    print("=== PDF Parser Demonstration ===\n")
    
    # Create sample PDF
    pdf_path = create_sample_pdf()
    print(f"Created sample PDF: {Path(pdf_path).name}\n")
    
    # Extract sections
    sections = extract_pdf_sections(pdf_path)
    
    print(f"Extracted {len(sections)} sections:\n")
    
    for section in sections:
        print(f"Section {section.section_number}: {section.section_title}")
        print(f"  Source: {section.source}")
        print(f"  Page: {section.page_number}")
        print(f"  Date: {section.doc_date.strftime('%Y-%m-%d')}")
        print(f"  Type: {section.doc_type}")
        print(f"  Content preview: {section.content[:50]}...")
        print()
    
    # Demonstrate date parsing
    print("\n=== Date Parsing Examples ===\n")
    test_filenames = [
        "Policy_2024-03-15.pdf",
        "Refund_Policy_March2024.pdf",
        "Document_20240315.pdf",
        "Report_Jan2024.pdf",
    ]
    
    for filename in test_filenames:
        date = parse_date_from_filename(filename)
        if date:
            print(f"{filename} → {date.strftime('%Y-%m-%d')}")
        else:
            print(f"{filename} → No date found")
    
    # Cleanup
    Path(pdf_path).unlink()
    print("\n✓ Demonstration complete")


if __name__ == "__main__":
    main()

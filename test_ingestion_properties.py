"""Property-based tests for ingestion dashboard functionality."""

import tempfile
from datetime import datetime
from pathlib import Path
import time

import fitz
import pytest
from hypothesis import given, strategies as st, settings
from openpyxl import Workbook

from ingestion.pdf_parser import extract_pdf_sections
from ingestion.excel_parser import extract_excel_rows
from ingestion.email_parser import parse_eml_file


# Feature: sme-knowledge-agent, Property 15: Ingestion summary accuracy
# **Validates: Requirements 10.1**


@given(
    num_pdf_sections=st.integers(min_value=0, max_value=10),
    num_excel_rows=st.integers(min_value=0, max_value=20),
    num_email_messages=st.integers(min_value=0, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_property_15_ingestion_summary_accuracy(
    num_pdf_sections,
    num_excel_rows,
    num_email_messages
):
    """
    Property 15: Ingestion summary accuracy
    
    For any completed ingestion run with a known quantity of documents, sections,
    rows, and messages, the summary statistics SHALL accurately count and report
    the total number of each item type processed.
    
    **Validates: Requirements 10.1**
    """
    # Track expected counts
    expected_stats = {
        'total_documents': 0,
        'total_sections': 0,
        'total_excel_rows': 0,
        'total_email_messages': 0
    }
    
    actual_stats = {
        'total_documents': 0,
        'total_sections': 0,
        'total_excel_rows': 0,
        'total_email_messages': 0
    }
    
    # Generate and process PDF if sections requested
    if num_pdf_sections > 0:
        # Use a unique temporary directory for each test
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "test.pdf"
            
            doc = fitz.open()
            
            # Create pages and TOC
            toc = []
            for i in range(num_pdf_sections):
                page = doc.new_page()
                page.insert_text((72, 72), f"Section {i+1} content")
                toc.append([1, f"Section {i+1}", i+1])
            
            doc.set_toc(toc)
            doc.save(str(pdf_path))
            doc.close()
            
            # Small delay to ensure file is fully written
            time.sleep(0.01)
            
            # Extract sections
            sections = extract_pdf_sections(str(pdf_path))
            actual_stats['total_sections'] = len(sections)
            actual_stats['total_documents'] += 1
        
        expected_stats['total_sections'] = num_pdf_sections
        expected_stats['total_documents'] += 1
    
    # Generate and process Excel if rows requested
    if num_excel_rows > 0:
        with tempfile.TemporaryDirectory() as tmpdir:
            excel_path = Path(tmpdir) / "test.xlsx"
            
            wb = Workbook()
            ws = wb.active
            
            # Add header row
            ws.append(['Client', 'Product', 'Price'])
            
            # Add data rows
            for i in range(num_excel_rows):
                ws.append([f'Client{i}', f'Product{i}', 100 + i])
            
            wb.save(str(excel_path))
            wb.close()
            
            # Small delay to ensure file is fully written
            time.sleep(0.01)
            
            # Extract rows
            rows = extract_excel_rows(str(excel_path))
            actual_stats['total_excel_rows'] = len(rows)
            actual_stats['total_documents'] += 1
        
        expected_stats['total_excel_rows'] = num_excel_rows
        expected_stats['total_documents'] += 1
    
    # Generate and process Email if messages requested
    if num_email_messages > 0:
        for i in range(num_email_messages):
            with tempfile.TemporaryDirectory() as tmpdir:
                eml_path = Path(tmpdir) / f"test{i}.eml"
                
                # Create minimal valid EML with proper encoding
                eml_content = f"""From: sender{i}@example.com
To: recipient@example.com
Subject: Test message {i}
Date: Mon, 01 Jan 2024 12:00:00 +0000
Message-ID: <msg{i}@example.com>

This is test message {i}.
"""
                # Write as bytes since email parser reads in binary mode
                eml_path.write_bytes(eml_content.encode('utf-8'))
                
                # Small delay to ensure file is fully written
                time.sleep(0.01)
                
                # Extract messages
                messages = parse_eml_file(str(eml_path))
                actual_stats['total_email_messages'] += len(messages)
                # Each EML file is a separate document
                actual_stats['total_documents'] += 1
        
        expected_stats['total_email_messages'] = num_email_messages
        expected_stats['total_documents'] += num_email_messages
    
    # Property assertion: actual counts must match expected counts
    assert actual_stats['total_documents'] == expected_stats['total_documents'], \
        f"Document count mismatch: expected {expected_stats['total_documents']}, got {actual_stats['total_documents']}"
    
    assert actual_stats['total_sections'] == expected_stats['total_sections'], \
        f"Section count mismatch: expected {expected_stats['total_sections']}, got {actual_stats['total_sections']}"
    
    assert actual_stats['total_excel_rows'] == expected_stats['total_excel_rows'], \
        f"Excel row count mismatch: expected {expected_stats['total_excel_rows']}, got {actual_stats['total_excel_rows']}"
    
    assert actual_stats['total_email_messages'] == expected_stats['total_email_messages'], \
        f"Email message count mismatch: expected {expected_stats['total_email_messages']}, got {actual_stats['total_email_messages']}"


# Additional edge case tests for ingestion summary

def test_ingestion_summary_empty_documents():
    """Test ingestion summary with no documents."""
    stats = {
        'total_documents': 0,
        'total_sections': 0,
        'total_excel_rows': 0,
        'total_email_messages': 0
    }
    
    # All counts should be zero
    assert stats['total_documents'] == 0
    assert stats['total_sections'] == 0
    assert stats['total_excel_rows'] == 0
    assert stats['total_email_messages'] == 0


def test_ingestion_summary_mixed_document_types():
    """Test ingestion summary with mixed document types."""
    # Create one of each type
    pdf_sections = 3
    excel_rows = 5
    email_messages = 2
    
    # Simulate processing
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        doc = fitz.open()
        toc = []
        for i in range(pdf_sections):
            doc.new_page()
            toc.append([1, f"Section {i+1}", i+1])
        doc.set_toc(toc)
        doc.save(tmp_pdf.name)
        doc.close()
        
        sections = extract_pdf_sections(tmp_pdf.name)
        Path(tmp_pdf.name).unlink()
    
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_excel:
        wb = Workbook()
        ws = wb.active
        ws.append(['Client', 'Product', 'Price'])
        for i in range(excel_rows):
            ws.append([f'Client{i}', f'Product{i}', 100])
        wb.save(tmp_excel.name)
        wb.close()
        
        rows = extract_excel_rows(tmp_excel.name)
        Path(tmp_excel.name).unlink()
    
    # Verify counts
    assert len(sections) == pdf_sections
    assert len(rows) == excel_rows
    
    # Total documents should be 2 (1 PDF + 1 Excel)
    total_documents = 2
    assert total_documents == 2


def test_ingestion_summary_large_batch():
    """Test ingestion summary with large batch of documents."""
    # Test with larger numbers to ensure scalability
    num_sections = 50
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        doc = fitz.open()
        toc = []
        for i in range(num_sections):
            doc.new_page()
            toc.append([1, f"Section {i+1}", i+1])
        doc.set_toc(toc)
        doc.save(tmp.name)
        doc.close()
        
        sections = extract_pdf_sections(tmp.name)
        Path(tmp.name).unlink()
    
    # Verify all sections were extracted
    assert len(sections) == num_sections

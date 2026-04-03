"""Unit tests for PDF parser module."""

import tempfile
from datetime import datetime
from pathlib import Path

import fitz
import pytest

from ingestion.pdf_parser import (
    PDFSection,
    extract_pdf_sections,
    parse_date_from_filename,
    parse_date_from_content,
    extract_toc_from_outline,
    extract_text_between_pages,
)


class TestParseDateFromFilename:
    """Test date extraction from various filename patterns."""
    
    def test_iso_date_format(self):
        """Test YYYY-MM-DD format."""
        result = parse_date_from_filename("Policy_2024-03-15.pdf")
        assert result == datetime(2024, 3, 15)
    
    def test_compact_date_format(self):
        """Test YYYYMMDD format."""
        result = parse_date_from_filename("Document_20240315.pdf")
        assert result == datetime(2024, 3, 15)
    
    def test_month_name_year_format(self):
        """Test Month+Year format."""
        result = parse_date_from_filename("Refund_Policy_v2_March2024.pdf")
        assert result == datetime(2024, 3, 1)
    
    def test_abbreviated_month_format(self):
        """Test abbreviated month names."""
        result = parse_date_from_filename("Policy_Jan2024.pdf")
        assert result == datetime(2024, 1, 1)
    
    def test_year_only_format(self):
        """Test year-only extraction."""
        result = parse_date_from_filename("Annual_Report_2024_Final.pdf")
        assert result == datetime(2024, 1, 1)
    
    def test_no_date_in_filename(self):
        """Test filename without date returns None."""
        result = parse_date_from_filename("Policy_Document.pdf")
        assert result is None
    
    def test_case_insensitive_month_names(self):
        """Test month names are case-insensitive."""
        result = parse_date_from_filename("Doc_MARCH2024.pdf")
        assert result == datetime(2024, 3, 1)


class TestExtractTocFromOutline:
    """Test TOC extraction from PDF outline."""
    
    def test_simple_toc_structure(self):
        """Test extraction of simple flat TOC."""
        # Create a minimal PDF with TOC
        doc = fitz.open()
        page1 = doc.new_page()
        page2 = doc.new_page()
        
        # Add TOC entries
        toc = [
            [1, "Introduction", 1],
            [1, "Methods", 2],
        ]
        doc.set_toc(toc)
        
        result = extract_toc_from_outline(doc)
        
        assert len(result) == 2
        assert result[0]['title'] == "Introduction"
        assert result[0]['section_number'] == "1"
        assert result[0]['page'] == 1
        assert result[1]['title'] == "Methods"
        assert result[1]['section_number'] == "2"
        
        doc.close()
    
    def test_hierarchical_toc_structure(self):
        """Test extraction of nested TOC with subsections."""
        doc = fitz.open()
        for _ in range(5):
            doc.new_page()
        
        toc = [
            [1, "Chapter 1", 1],
            [2, "Section 1.1", 2],
            [2, "Section 1.2", 3],
            [1, "Chapter 2", 4],
            [2, "Section 2.1", 5],
        ]
        doc.set_toc(toc)
        
        result = extract_toc_from_outline(doc)
        
        assert len(result) == 5
        assert result[0]['section_number'] == "1"
        assert result[1]['section_number'] == "1.1"
        assert result[2]['section_number'] == "1.2"
        assert result[3]['section_number'] == "2"
        assert result[4]['section_number'] == "2.1"
        
        doc.close()
    
    def test_empty_toc(self):
        """Test PDF without TOC returns empty list."""
        doc = fitz.open()
        doc.new_page()
        
        result = extract_toc_from_outline(doc)
        
        assert result == []
        doc.close()


class TestExtractTextBetweenPages:
    """Test text extraction between page ranges."""
    
    def test_single_page_extraction(self):
        """Test extracting text from a single page."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Test content on page 1")
        
        result = extract_text_between_pages(doc, 1, 2)
        
        assert "Test content on page 1" in result
        doc.close()
    
    def test_multiple_page_extraction(self):
        """Test extracting text across multiple pages."""
        doc = fitz.open()
        page1 = doc.new_page()
        page1.insert_text((72, 72), "Page 1 content")
        page2 = doc.new_page()
        page2.insert_text((72, 72), "Page 2 content")
        
        result = extract_text_between_pages(doc, 1, 3)
        
        assert "Page 1 content" in result
        assert "Page 2 content" in result
        doc.close()


class TestExtractPdfSections:
    """Test complete PDF section extraction."""
    
    def test_pdf_with_toc(self):
        """Test extraction from PDF with table of contents."""
        # Create temporary PDF with TOC
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            doc = fitz.open()
            page1 = doc.new_page()
            page1.insert_text((72, 72), "Introduction content")
            page2 = doc.new_page()
            page2.insert_text((72, 72), "Methods content")
            
            toc = [
                [1, "Introduction", 1],
                [1, "Methods", 2],
            ]
            doc.set_toc(toc)
            doc.save(tmp.name)
            doc.close()
            
            # Test extraction
            sections = extract_pdf_sections(tmp.name)
            
            assert len(sections) == 2
            assert sections[0].section_title == "Introduction"
            assert sections[0].section_number == "1"
            assert sections[0].page_number == 1
            assert "Introduction content" in sections[0].content
            assert sections[0].doc_type == "policy"
            
            assert sections[1].section_title == "Methods"
            assert sections[1].section_number == "2"
            
            # Cleanup
            Path(tmp.name).unlink()
    
    def test_pdf_without_toc_fallback(self):
        """Test fallback behavior for PDF without TOC."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((72, 72), "Full document content")
            doc.save(tmp.name)
            doc.close()
            
            sections = extract_pdf_sections(tmp.name)
            
            assert len(sections) == 1
            assert sections[0].section_title == "Full Document"
            assert sections[0].section_number == "1"
            assert "Full document content" in sections[0].content
            
            Path(tmp.name).unlink()
    
    def test_date_extraction_from_filename(self):
        """Test that doc_date is extracted from filename."""
        with tempfile.NamedTemporaryFile(
            suffix=".pdf", 
            prefix="Policy_2024-03-15_",
            delete=False
        ) as tmp:
            doc = fitz.open()
            doc.new_page()
            doc.save(tmp.name)
            doc.close()
            
            sections = extract_pdf_sections(tmp.name)
            
            assert sections[0].doc_date == datetime(2024, 3, 15)
            
            Path(tmp.name).unlink()
    
    def test_hierarchical_section_numbering(self):
        """Test hierarchical section numbering (e.g., 2.3.1)."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            doc = fitz.open()
            for _ in range(4):
                doc.new_page()
            
            toc = [
                [1, "Chapter 1", 1],
                [2, "Section 1.1", 2],
                [3, "Subsection 1.1.1", 3],
                [1, "Chapter 2", 4],
            ]
            doc.set_toc(toc)
            doc.save(tmp.name)
            doc.close()
            
            sections = extract_pdf_sections(tmp.name)
            
            assert sections[0].section_number == "1"
            assert sections[1].section_number == "1.1"
            assert sections[2].section_number == "1.1.1"
            assert sections[3].section_number == "2"
            
            Path(tmp.name).unlink()

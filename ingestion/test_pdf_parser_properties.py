"""Property-based tests for PDF parser module using Hypothesis.

Feature: sme-knowledge-agent
"""

import tempfile
from datetime import datetime
from pathlib import Path

import fitz
import pytest
from hypothesis import given, strategies as st, settings

from ingestion.pdf_parser import (
    parse_date_from_filename,
    extract_pdf_sections,
    extract_toc_from_outline,
)


# Custom strategies for generating test data
@st.composite
def filename_with_iso_date(draw):
    """Generate filename with ISO date format (YYYY-MM-DD)."""
    year = draw(st.integers(min_value=2000, max_value=2030))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))  # Safe day range
    prefix = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=10))
    return f"{prefix}_{year:04d}-{month:02d}-{day:02d}.pdf", datetime(year, month, day)


@st.composite
def filename_with_month_year(draw):
    """Generate filename with Month+Year format."""
    year = draw(st.integers(min_value=2000, max_value=2030))
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_idx = draw(st.integers(min_value=0, max_value=11))
    month_name = month_names[month_idx]
    prefix = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=10))
    return f"{prefix}_{month_name}{year}.pdf", datetime(year, month_idx + 1, 1)


@st.composite
def toc_structure(draw):
    """Generate valid TOC structure."""
    num_entries = draw(st.integers(min_value=1, max_value=10))
    toc = []
    for i in range(num_entries):
        level = draw(st.integers(min_value=1, max_value=3))
        title = draw(st.text(min_size=1, max_size=50))
        page = i + 1
        toc.append([level, title, page])
    return toc


# Property 1: PDF TOC extraction completeness
# **Validates: Requirements 1.1**
@given(toc_structure())
@settings(max_examples=20)
def test_property_toc_extraction_completeness(toc_entries):
    """
    Property 1: PDF TOC extraction completeness
    
    For any valid PDF file with a table of contents, the extraction process
    SHALL identify and extract all named sections with their hierarchical
    structure preserved.
    
    **Validates: Requirements 1.1**
    """
    # Create PDF with given TOC structure
    doc = fitz.open()
    for _ in range(len(toc_entries)):
        doc.new_page()
    doc.set_toc(toc_entries)
    
    # Extract TOC
    result = extract_toc_from_outline(doc)
    doc.close()
    
    # Property: All TOC entries must be extracted
    assert len(result) == len(toc_entries), \
        f"Expected {len(toc_entries)} sections, got {len(result)}"
    
    # Property: All titles must be preserved
    for i, entry in enumerate(toc_entries):
        assert result[i]['title'] == entry[1].strip(), \
            f"Title mismatch at index {i}: expected '{entry[1]}', got '{result[i]['title']}'"
    
    # Property: All page numbers must be preserved
    for i, entry in enumerate(toc_entries):
        assert result[i]['page'] == entry[2], \
            f"Page number mismatch at index {i}: expected {entry[2]}, got {result[i]['page']}"
    
    # Property: Section numbers must be hierarchical and non-empty
    for i, section in enumerate(result):
        assert section['section_number'], \
            f"Section number is empty at index {i}"
        assert all(part.isdigit() for part in section['section_number'].split('.')), \
            f"Section number contains non-numeric parts: {section['section_number']}"


# Property 3: Filename date extraction accuracy
# **Validates: Requirements 1.3**
@given(filename_with_iso_date())
@settings(max_examples=20)
def test_property_filename_date_extraction_iso(filename_and_date):
    """
    Property 3: Filename date extraction accuracy (ISO format)
    
    For any filename containing a date pattern (e.g., "Policy_2024-03-15.pdf"),
    the date extraction function SHALL parse and return the correct date value.
    
    **Validates: Requirements 1.3**
    """
    filename, expected_date = filename_and_date
    
    result = parse_date_from_filename(filename)
    
    # Property: Date must be extracted correctly
    assert result is not None, f"Failed to extract date from filename: {filename}"
    assert result == expected_date, \
        f"Date mismatch for {filename}: expected {expected_date}, got {result}"


@given(filename_with_month_year())
@settings(max_examples=20)
def test_property_filename_date_extraction_month_year(filename_and_date):
    """
    Property 3: Filename date extraction accuracy (Month+Year format)
    
    For any filename containing a date pattern (e.g., "Policy_March2024.pdf"),
    the date extraction function SHALL parse and return the correct date value.
    
    **Validates: Requirements 1.3**
    """
    filename, expected_date = filename_and_date
    
    result = parse_date_from_filename(filename)
    
    # Property: Date must be extracted correctly
    assert result is not None, f"Failed to extract date from filename: {filename}"
    assert result == expected_date, \
        f"Date mismatch for {filename}: expected {expected_date}, got {result}"


# Property: Complete PDF section extraction
@given(
    st.lists(
        st.tuples(
            st.integers(min_value=1, max_value=2),  # level
            st.text(min_size=1, max_size=30),  # title
        ),
        min_size=1,
        max_size=5
    )
)
@settings(max_examples=50)
def test_property_pdf_section_extraction_complete(toc_data):
    """
    Property: For any PDF with TOC, extract_pdf_sections returns all sections.
    
    **Validates: Requirements 1.1**
    """
    with tempfile.NamedTemporaryFile(suffix="_2024-01-01.pdf", delete=False) as tmp:
        doc = fitz.open()
        
        # Create pages and TOC
        toc = []
        for i, (level, title) in enumerate(toc_data):
            doc.new_page()
            toc.append([level, title, i + 1])
        
        doc.set_toc(toc)
        doc.save(tmp.name)
        doc.close()
        
        # Extract sections
        sections = extract_pdf_sections(tmp.name)
        
        # Property: Number of sections matches TOC entries
        assert len(sections) == len(toc_data), \
            f"Expected {len(toc_data)} sections, got {len(sections)}"
        
        # Property: All sections have required metadata fields
        for section in sections:
            assert section.source, "Section missing source"
            assert section.section_title, "Section missing title"
            assert section.section_number, "Section missing number"
            assert section.page_number > 0, "Invalid page number"
            assert section.doc_date, "Section missing doc_date"
            assert section.doc_type == "policy", "Incorrect doc_type"
            assert section.content is not None, "Section missing content"
        
        # Cleanup
        Path(tmp.name).unlink()

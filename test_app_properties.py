"""
Property-based tests for app.py citation formatting.

Tests Property 7: Citation formatting completeness.
"""

from hypothesis import given, strategies as st, settings
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import render_citation


# ============================================================================
# Hypothesis Strategies for Document Chunks
# ============================================================================

@st.composite
def pdf_chunk(draw):
    """Generate a PDF chunk with metadata."""
    source = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='._-'
    )))
    if not source.endswith('.pdf'):
        source += '.pdf'
    
    section_title = draw(st.text(min_size=3, max_size=50))
    section_number = draw(st.text(min_size=1, max_size=10, alphabet=st.characters(
        whitelist_categories=('Nd',), whitelist_characters='.'
    )))
    page_number = draw(st.integers(min_value=1, max_value=1000))
    
    return {
        'content': draw(st.text(min_size=10, max_size=200)),
        'metadata': {
            'source': source,
            'doc_type': 'policy',
            'section_title': section_title,
            'section_number': section_number,
            'page_number': page_number,
            'doc_date': '2024-01-15'
        }
    }


@st.composite
def excel_chunk(draw):
    """Generate an Excel chunk with metadata."""
    source = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='._-'
    )))
    if not source.endswith('.xlsx'):
        source += '.xlsx'
    
    sheet_name = draw(st.text(min_size=1, max_size=30))
    row_number = draw(st.integers(min_value=1, max_value=10000))
    
    return {
        'content': draw(st.text(min_size=10, max_size=200)),
        'metadata': {
            'source': source,
            'doc_type': 'excel',
            'sheet_name': sheet_name,
            'row_number': row_number,
            'client': draw(st.text(min_size=3, max_size=30)),
            'doc_date': '2024-01-15'
        }
    }


@st.composite
def email_chunk(draw):
    """Generate an email chunk with metadata."""
    # Generate email address
    username = draw(st.text(min_size=3, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='._-'
    )))
    domain = draw(st.text(min_size=3, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-'
    )))
    sender = f"{username}@{domain}.com"
    
    subject = draw(st.text(min_size=5, max_size=100))
    doc_date = draw(st.dates(min_value=datetime(2020, 1, 1).date(), 
                             max_value=datetime(2024, 12, 31).date()))
    
    return {
        'content': draw(st.text(min_size=10, max_size=200)),
        'metadata': {
            'source': 'email_thread.eml',
            'doc_type': 'email',
            'sender': sender,
            'subject': subject,
            'doc_date': doc_date.isoformat(),
            'thread_id': draw(st.text(min_size=10, max_size=20))
        }
    }


# ============================================================================
# Property-Based Tests
# ============================================================================

# Feature: sme-knowledge-agent, Property 7: Citation formatting completeness
@given(chunk=pdf_chunk())
@settings(max_examples=100)
def test_property_pdf_citation_completeness(chunk):
    """
    Property 7: Citation formatting completeness for PDF chunks.
    
    For any PDF chunk with metadata, the citation formatting function SHALL
    include all required fields (filename, section identifiers, page number)
    in the output string.
    
    Validates: Requirements 5.1
    """
    citation = render_citation(chunk)
    
    # Citation must be non-empty
    assert len(citation) > 0
    
    # Citation must include source filename
    assert chunk['metadata']['source'] in citation
    
    # Citation must include section information if present
    section_title = chunk['metadata'].get('section_title', '')
    section_number = chunk['metadata'].get('section_number', '')
    
    if section_title:
        assert section_title in citation
    
    if section_number:
        assert section_number in citation
    
    # Citation must include page number
    page_number = chunk['metadata'].get('page_number')
    if page_number:
        assert str(page_number) in citation


# Feature: sme-knowledge-agent, Property 7: Citation formatting completeness
@given(chunk=excel_chunk())
@settings(max_examples=100)
def test_property_excel_citation_completeness(chunk):
    """
    Property 7: Citation formatting completeness for Excel chunks.
    
    For any Excel chunk with metadata, the citation formatting function SHALL
    include all required fields (filename, sheet name, row number) in the
    output string.
    
    Validates: Requirements 5.2
    """
    citation = render_citation(chunk)
    
    # Citation must be non-empty
    assert len(citation) > 0
    
    # Citation must include source filename
    assert chunk['metadata']['source'] in citation
    
    # Citation must include sheet name
    sheet_name = chunk['metadata'].get('sheet_name', '')
    if sheet_name:
        assert sheet_name in citation
    
    # Citation must include row number
    row_number = chunk['metadata'].get('row_number')
    if row_number:
        assert str(row_number) in citation


# Feature: sme-knowledge-agent, Property 7: Citation formatting completeness
@given(chunk=email_chunk())
@settings(max_examples=100)
def test_property_email_citation_completeness(chunk):
    """
    Property 7: Citation formatting completeness for Email chunks.
    
    For any email chunk with metadata, the citation formatting function SHALL
    include all required fields (sender, date, subject) in the output string.
    
    Validates: Requirements 5.3
    """
    citation = render_citation(chunk)
    
    # Citation must be non-empty
    assert len(citation) > 0
    
    # Citation must include sender
    sender = chunk['metadata'].get('sender', '')
    if sender:
        assert sender in citation
    
    # Citation must include date
    doc_date = chunk['metadata'].get('doc_date', '')
    if doc_date:
        # Extract date part (YYYY-MM-DD)
        date_part = doc_date.split('T')[0] if 'T' in doc_date else doc_date
        assert date_part in citation
    
    # Citation must include subject
    subject = chunk['metadata'].get('subject', '')
    if subject:
        assert subject in citation


# Feature: sme-knowledge-agent, Property 7: Citation formatting completeness
@given(
    doc_type=st.sampled_from(['policy', 'excel', 'email']),
    source=st.text(min_size=5, max_size=50)
)
@settings(max_examples=100)
def test_property_citation_always_includes_source(doc_type, source):
    """
    Property 7: Citation always includes source filename.
    
    For any document chunk regardless of doc_type, the citation SHALL
    always include the source filename.
    
    Validates: Requirements 5.1, 5.2, 5.3
    """
    chunk = {
        'content': 'Test content',
        'metadata': {
            'source': source,
            'doc_type': doc_type
        }
    }
    
    citation = render_citation(chunk)
    
    # Citation must be non-empty
    assert len(citation) > 0
    
    # Citation must include source
    assert source in citation


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])

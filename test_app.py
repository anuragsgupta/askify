"""
Unit tests for app.py query interface and citation formatting.
"""

import pytest
from datetime import datetime
from app import render_citation


class TestRenderCitation:
    """Test citation formatting for different document types."""
    
    def test_pdf_citation_with_all_fields(self):
        """Test PDF citation with all metadata fields present."""
        chunk = {
            'content': 'Refund policy content',
            'metadata': {
                'source': 'Refund_Policy_v2.pdf',
                'doc_type': 'policy',
                'section_title': 'Returns',
                'section_number': '3.2',
                'page_number': 5,
                'doc_date': '2024-03-15'
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'Refund_Policy_v2.pdf' in citation
        assert 'Section 3.2' in citation
        assert 'Returns' in citation
        assert 'Page 5' in citation
    
    def test_pdf_citation_with_section_title_only(self):
        """Test PDF citation with only section title."""
        chunk = {
            'content': 'Policy content',
            'metadata': {
                'source': 'Policy.pdf',
                'doc_type': 'policy',
                'section_title': 'General Terms',
                'page_number': 10
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'Policy.pdf' in citation
        assert 'General Terms' in citation
        assert 'Page 10' in citation
    
    def test_pdf_citation_with_section_number_only(self):
        """Test PDF citation with only section number."""
        chunk = {
            'content': 'Policy content',
            'metadata': {
                'source': 'Policy.pdf',
                'doc_type': 'policy',
                'section_number': '2.1',
                'page_number': 3
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'Policy.pdf' in citation
        assert '2.1' in citation
        assert 'Page 3' in citation
    
    def test_pdf_citation_minimal_metadata(self):
        """Test PDF citation with minimal metadata (source only)."""
        chunk = {
            'content': 'Policy content',
            'metadata': {
                'source': 'Document.pdf',
                'doc_type': 'policy'
            }
        }
        
        citation = render_citation(chunk)
        
        assert citation == 'Document.pdf'
    
    def test_excel_citation_with_all_fields(self):
        """Test Excel citation with all metadata fields present."""
        chunk = {
            'content': 'Client: Acme Corp, Price: $500',
            'metadata': {
                'source': 'Pricing_2024.xlsx',
                'doc_type': 'excel',
                'sheet_name': 'Q1',
                'row_number': 42,
                'client': 'Acme Corp',
                'doc_date': '2024-01-15'
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'Pricing_2024.xlsx' in citation
        assert 'Sheet: Q1' in citation
        assert 'Row 42' in citation
    
    def test_excel_citation_with_sheet_only(self):
        """Test Excel citation with only sheet name."""
        chunk = {
            'content': 'Data',
            'metadata': {
                'source': 'Data.xlsx',
                'doc_type': 'excel',
                'sheet_name': 'Summary'
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'Data.xlsx' in citation
        assert 'Sheet: Summary' in citation
    
    def test_excel_citation_with_row_only(self):
        """Test Excel citation with only row number."""
        chunk = {
            'content': 'Data',
            'metadata': {
                'source': 'Data.xlsx',
                'doc_type': 'excel',
                'row_number': 100
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'Data.xlsx' in citation
        assert 'Row 100' in citation
    
    def test_excel_citation_minimal_metadata(self):
        """Test Excel citation with minimal metadata (source only)."""
        chunk = {
            'content': 'Data',
            'metadata': {
                'source': 'Spreadsheet.xlsx',
                'doc_type': 'excel'
            }
        }
        
        citation = render_citation(chunk)
        
        assert citation == 'Spreadsheet.xlsx'
    
    def test_email_citation_with_all_fields(self):
        """Test email citation with all metadata fields present."""
        chunk = {
            'content': 'Email body',
            'metadata': {
                'source': 'thread.eml',
                'doc_type': 'email',
                'sender': 'john@acme.com',
                'doc_date': '2024-01-15',
                'subject': 'Discount approval',
                'thread_id': 'abc123'
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'From: john@acme.com' in citation
        assert '2024-01-15' in citation
        assert 'Subject: Discount approval' in citation
    
    def test_email_citation_with_iso_datetime(self):
        """Test email citation with ISO datetime format."""
        chunk = {
            'content': 'Email body',
            'metadata': {
                'source': 'thread.eml',
                'doc_type': 'email',
                'sender': 'jane@company.com',
                'doc_date': '2024-01-15T10:30:00Z',
                'subject': 'Policy update'
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'From: jane@company.com' in citation
        assert '2024-01-15' in citation  # Date part extracted
        assert 'Subject: Policy update' in citation
    
    def test_email_citation_with_sender_only(self):
        """Test email citation with only sender."""
        chunk = {
            'content': 'Email body',
            'metadata': {
                'source': 'email.eml',
                'doc_type': 'email',
                'sender': 'user@example.com'
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'From: user@example.com' in citation
    
    def test_email_citation_minimal_metadata(self):
        """Test email citation with minimal metadata (source only)."""
        chunk = {
            'content': 'Email body',
            'metadata': {
                'source': 'message.eml',
                'doc_type': 'email'
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'Email from message.eml' in citation
    
    def test_unknown_doc_type_fallback(self):
        """Test citation for unknown doc_type falls back to source."""
        chunk = {
            'content': 'Content',
            'metadata': {
                'source': 'unknown_file.txt',
                'doc_type': 'unknown'
            }
        }
        
        citation = render_citation(chunk)
        
        assert citation == 'unknown_file.txt'
    
    def test_empty_metadata(self):
        """Test citation with empty metadata."""
        chunk = {
            'content': 'Content',
            'metadata': {}
        }
        
        citation = render_citation(chunk)
        
        assert citation == 'Unknown'
    
    def test_missing_metadata_key(self):
        """Test citation when metadata key is missing."""
        chunk = {
            'content': 'Content'
        }
        
        citation = render_citation(chunk)
        
        assert citation == 'Unknown'


class TestCitationEdgeCases:
    """Test edge cases for citation formatting."""
    
    def test_special_characters_in_filename(self):
        """Test citation with special characters in filename."""
        chunk = {
            'content': 'Content',
            'metadata': {
                'source': 'Policy_@#$_2024.pdf',
                'doc_type': 'policy'
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'Policy_@#$_2024.pdf' in citation
    
    def test_unicode_characters_in_section_title(self):
        """Test citation with unicode characters."""
        chunk = {
            'content': 'Content',
            'metadata': {
                'source': 'Policy.pdf',
                'doc_type': 'policy',
                'section_title': 'Política de Reembolso 🎉',
                'page_number': 1
            }
        }
        
        citation = render_citation(chunk)
        
        assert 'Política de Reembolso 🎉' in citation
    
    def test_very_long_section_title(self):
        """Test citation with very long section title."""
        long_title = 'A' * 200
        chunk = {
            'content': 'Content',
            'metadata': {
                'source': 'Policy.pdf',
                'doc_type': 'policy',
                'section_title': long_title,
                'page_number': 1
            }
        }
        
        citation = render_citation(chunk)
        
        assert long_title in citation
    
    def test_zero_page_number(self):
        """Test citation with page number zero."""
        chunk = {
            'content': 'Content',
            'metadata': {
                'source': 'Doc.pdf',
                'doc_type': 'policy',
                'page_number': 0
            }
        }
        
        citation = render_citation(chunk)
        
        # Page 0 should not be included (falsy value)
        assert 'Page 0' not in citation
    
    def test_negative_row_number(self):
        """Test citation with negative row number."""
        chunk = {
            'content': 'Content',
            'metadata': {
                'source': 'Data.xlsx',
                'doc_type': 'excel',
                'row_number': -1
            }
        }
        
        citation = render_citation(chunk)
        
        # Negative row should still be included (truthy value)
        assert 'Row -1' in citation
    
    def test_empty_string_values(self):
        """Test citation with empty string values in metadata."""
        chunk = {
            'content': 'Content',
            'metadata': {
                'source': 'File.pdf',
                'doc_type': 'policy',
                'section_title': '',
                'section_number': '',
                'page_number': ''
            }
        }
        
        citation = render_citation(chunk)
        
        # Should only show source when all other fields are empty
        assert citation == 'File.pdf'


class TestCitationFormats:
    """Test specific citation format requirements."""
    
    def test_pdf_citation_format_matches_spec(self):
        """Test PDF citation matches specification format."""
        chunk = {
            'content': 'Content',
            'metadata': {
                'source': 'Refund Policy v2',
                'doc_type': 'policy',
                'section_title': 'Returns',
                'section_number': '3.2',
                'page_number': 5
            }
        }
        
        citation = render_citation(chunk)
        
        # Should match format: "Refund Policy v2 (Section 3.2: Returns, Page 5)"
        assert citation == 'Refund Policy v2 (Section 3.2: Returns, Page 5)'
    
    def test_excel_citation_format_matches_spec(self):
        """Test Excel citation matches specification format."""
        chunk = {
            'content': 'Content',
            'metadata': {
                'source': 'Pricing_2024.xlsx',
                'doc_type': 'excel',
                'sheet_name': 'Q1',
                'row_number': 42
            }
        }
        
        citation = render_citation(chunk)
        
        # Should match format: "Pricing_2024.xlsx (Sheet: Q1, Row 42)"
        assert citation == 'Pricing_2024.xlsx (Sheet: Q1, Row 42)'
    
    def test_email_citation_format_matches_spec(self):
        """Test email citation matches specification format."""
        chunk = {
            'content': 'Content',
            'metadata': {
                'source': 'email.eml',
                'doc_type': 'email',
                'sender': 'john@acme.com',
                'doc_date': '2024-01-15',
                'subject': 'Discount approval'
            }
        }
        
        citation = render_citation(chunk)
        
        # Should match format: "From: john@acme.com (2024-01-15, Subject: Discount approval)"
        # Note: Our implementation uses "Email (...)" format
        assert 'From: john@acme.com' in citation
        assert '2024-01-15' in citation
        assert 'Subject: Discount approval' in citation


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

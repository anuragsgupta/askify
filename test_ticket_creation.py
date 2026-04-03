"""
Unit tests for ticket creation functionality.

Tests specific examples and edge cases for ticket pre-population.
"""

import pytest
from datetime import datetime


# ============================================================================
# Helper Functions (copied from property tests for unit testing)
# ============================================================================

def extract_client_name_from_context(query_context: dict) -> str:
    """
    Extract client name from Excel metadata in query context.
    Mimics the logic in render_ticket_creation().
    """
    for chunk in query_context.get('source_chunks', []):
        metadata = chunk.get('metadata', {})
        if metadata.get('doc_type') == 'excel' and metadata.get('client'):
            return metadata['client']
    return None


def create_ticket_data(query_context: dict, client_name: str) -> dict:
    """
    Create ticket data structure from query context.
    Mimics the logic in render_ticket_creation().
    """
    conflicts = query_context.get('conflicts', [])
    conflict_flag = len(conflicts) > 0
    resolution_reasoning = ""
    
    if conflict_flag:
        resolution_reasoning = "\n\n".join([
            f"Conflict {i+1}: {conflict.diff_explanation}"
            for i, conflict in enumerate(conflicts)
        ])
    
    return {
        'client_name': client_name,
        'query_text': query_context.get('query_text', ''),
        'ai_answer': query_context.get('ai_answer', ''),
        'source_citations': query_context.get('source_citations', []),
        'conflict_flag': conflict_flag,
        'resolution_reasoning': resolution_reasoning if conflict_flag else None,
        'created_at': datetime.now().isoformat()
    }


# ============================================================================
# Unit Tests for Ticket Pre-population
# ============================================================================

class TestTicketPrePopulation:
    """Test ticket pre-population with query context."""
    
    def test_ticket_with_complete_query_context(self):
        """Test ticket creation with complete query context."""
        query_context = {
            'query_text': 'What is our refund policy?',
            'ai_answer': 'Our refund policy allows returns within 60 days.',
            'source_citations': [
                'Refund_Policy_v2.pdf (Section 3.2: Returns, Page 5)',
                'Pricing_2024.xlsx (Sheet: Q1, Row 42)'
            ],
            'conflicts': [],
            'source_chunks': [
                {
                    'content': 'Refund policy content',
                    'metadata': {
                        'source': 'Refund_Policy_v2.pdf',
                        'doc_type': 'policy',
                        'section_title': 'Returns',
                        'page_number': 5
                    }
                },
                {
                    'content': 'Client: Acme Corp, Price: $500',
                    'metadata': {
                        'source': 'Pricing_2024.xlsx',
                        'doc_type': 'excel',
                        'client': 'Acme Corp',
                        'sheet_name': 'Q1',
                        'row_number': 42
                    }
                }
            ]
        }
        
        # Extract client name
        client_name = extract_client_name_from_context(query_context)
        assert client_name == 'Acme Corp'
        
        # Create ticket
        ticket_data = create_ticket_data(query_context, client_name)
        
        # Verify all fields
        assert ticket_data['client_name'] == 'Acme Corp'
        assert ticket_data['query_text'] == 'What is our refund policy?'
        assert ticket_data['ai_answer'] == 'Our refund policy allows returns within 60 days.'
        assert len(ticket_data['source_citations']) == 2
        assert ticket_data['conflict_flag'] == False
        assert ticket_data['resolution_reasoning'] is None
    
    def test_ticket_with_conflict_resolved(self):
        """Test ticket creation when conflict was resolved."""
        # Create mock conflict object
        conflict = type('Conflict', (), {
            'diff_explanation': 'Refund window changed from 30 to 60 days',
            'conflict_type': 'version_update'
        })()
        
        query_context = {
            'query_text': 'What is the refund window?',
            'ai_answer': 'The refund window is 60 days.',
            'source_citations': [
                'Refund_Policy_v2.pdf (Section 3.2: Returns, Page 5)'
            ],
            'conflicts': [conflict],
            'source_chunks': [
                {
                    'content': 'Refund policy content',
                    'metadata': {
                        'source': 'Refund_Policy_v2.pdf',
                        'doc_type': 'policy',
                        'section_title': 'Returns',
                        'page_number': 5
                    }
                }
            ]
        }
        
        client_name = 'Test Client'
        ticket_data = create_ticket_data(query_context, client_name)
        
        # Verify conflict fields
        assert ticket_data['conflict_flag'] == True
        assert ticket_data['resolution_reasoning'] is not None
        assert 'Refund window changed from 30 to 60 days' in ticket_data['resolution_reasoning']
        assert 'Conflict 1:' in ticket_data['resolution_reasoning']
    
    def test_ticket_with_multiple_conflicts(self):
        """Test ticket creation with multiple conflicts."""
        conflict1 = type('Conflict', (), {
            'diff_explanation': 'Refund window changed from 30 to 60 days',
            'conflict_type': 'version_update'
        })()
        
        conflict2 = type('Conflict', (), {
            'diff_explanation': 'Shipping fee changed from $10 to $15',
            'conflict_type': 'policy_change'
        })()
        
        query_context = {
            'query_text': 'What are our policies?',
            'ai_answer': 'Our policies have been updated.',
            'source_citations': ['Policy.pdf (Section 1, Page 1)'],
            'conflicts': [conflict1, conflict2],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Client')
        
        # Verify both conflicts are in resolution reasoning
        assert ticket_data['conflict_flag'] == True
        assert 'Conflict 1:' in ticket_data['resolution_reasoning']
        assert 'Conflict 2:' in ticket_data['resolution_reasoning']
        assert 'Refund window changed from 30 to 60 days' in ticket_data['resolution_reasoning']
        assert 'Shipping fee changed from $10 to $15' in ticket_data['resolution_reasoning']
    
    def test_ticket_with_empty_source_citations(self):
        """Test ticket creation with no source citations."""
        query_context = {
            'query_text': 'Test query',
            'ai_answer': 'Test answer',
            'source_citations': [],
            'conflicts': [],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Client')
        
        assert ticket_data['source_citations'] == []
        assert ticket_data['conflict_flag'] == False


class TestClientNameExtraction:
    """Test client name extraction from Excel metadata."""
    
    def test_extract_client_from_single_excel_chunk(self):
        """Test extracting client name from single Excel chunk."""
        query_context = {
            'source_chunks': [
                {
                    'content': 'Client: Acme Corp, Price: $500',
                    'metadata': {
                        'source': 'Pricing.xlsx',
                        'doc_type': 'excel',
                        'client': 'Acme Corp',
                        'row_number': 10
                    }
                }
            ]
        }
        
        client_name = extract_client_name_from_context(query_context)
        assert client_name == 'Acme Corp'
    
    def test_extract_client_from_multiple_excel_chunks(self):
        """Test extracting client name when multiple Excel chunks exist."""
        query_context = {
            'source_chunks': [
                {
                    'content': 'Policy content',
                    'metadata': {
                        'source': 'Policy.pdf',
                        'doc_type': 'policy'
                    }
                },
                {
                    'content': 'Client: First Corp, Price: $100',
                    'metadata': {
                        'source': 'Pricing.xlsx',
                        'doc_type': 'excel',
                        'client': 'First Corp',
                        'row_number': 5
                    }
                },
                {
                    'content': 'Client: Second Corp, Price: $200',
                    'metadata': {
                        'source': 'Pricing.xlsx',
                        'doc_type': 'excel',
                        'client': 'Second Corp',
                        'row_number': 10
                    }
                }
            ]
        }
        
        # Should return first Excel client found
        client_name = extract_client_name_from_context(query_context)
        assert client_name == 'First Corp'
    
    def test_extract_client_with_no_excel_chunks(self):
        """Test client extraction when no Excel chunks exist."""
        query_context = {
            'source_chunks': [
                {
                    'content': 'Policy content',
                    'metadata': {
                        'source': 'Policy.pdf',
                        'doc_type': 'policy',
                        'section_title': 'Returns'
                    }
                },
                {
                    'content': 'Email content',
                    'metadata': {
                        'source': 'email.eml',
                        'doc_type': 'email',
                        'sender': 'user@example.com'
                    }
                }
            ]
        }
        
        client_name = extract_client_name_from_context(query_context)
        assert client_name is None
    
    def test_extract_client_with_excel_chunk_missing_client_field(self):
        """Test client extraction when Excel chunk has no client field."""
        query_context = {
            'source_chunks': [
                {
                    'content': 'Data without client',
                    'metadata': {
                        'source': 'Data.xlsx',
                        'doc_type': 'excel',
                        'sheet_name': 'Summary',
                        'row_number': 1
                    }
                }
            ]
        }
        
        client_name = extract_client_name_from_context(query_context)
        assert client_name is None
    
    def test_extract_client_with_empty_source_chunks(self):
        """Test client extraction with empty source chunks list."""
        query_context = {
            'source_chunks': []
        }
        
        client_name = extract_client_name_from_context(query_context)
        assert client_name is None
    
    def test_extract_client_with_missing_source_chunks_key(self):
        """Test client extraction when source_chunks key is missing."""
        query_context = {
            'query_text': 'Test query',
            'ai_answer': 'Test answer'
        }
        
        client_name = extract_client_name_from_context(query_context)
        assert client_name is None


class TestConflictFlagSetting:
    """Test conflict_flag setting in ticket data."""
    
    def test_conflict_flag_true_with_single_conflict(self):
        """Test conflict_flag is True when one conflict exists."""
        conflict = type('Conflict', (), {
            'diff_explanation': 'Test conflict',
            'conflict_type': 'version_update'
        })()
        
        query_context = {
            'query_text': 'Test',
            'ai_answer': 'Test',
            'source_citations': [],
            'conflicts': [conflict],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Client')
        assert ticket_data['conflict_flag'] == True
    
    def test_conflict_flag_false_with_no_conflicts(self):
        """Test conflict_flag is False when no conflicts exist."""
        query_context = {
            'query_text': 'Test',
            'ai_answer': 'Test',
            'source_citations': [],
            'conflicts': [],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Client')
        assert ticket_data['conflict_flag'] == False
    
    def test_conflict_flag_true_with_multiple_conflicts(self):
        """Test conflict_flag is True with multiple conflicts."""
        conflicts = [
            type('Conflict', (), {'diff_explanation': 'Conflict 1', 'conflict_type': 'version_update'})(),
            type('Conflict', (), {'diff_explanation': 'Conflict 2', 'conflict_type': 'policy_change'})()
        ]
        
        query_context = {
            'query_text': 'Test',
            'ai_answer': 'Test',
            'source_citations': [],
            'conflicts': conflicts,
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Client')
        assert ticket_data['conflict_flag'] == True


class TestTicketDataStructure:
    """Test ticket data structure and field presence."""
    
    def test_ticket_has_all_required_fields(self):
        """Test ticket data contains all required fields."""
        query_context = {
            'query_text': 'Test query',
            'ai_answer': 'Test answer',
            'source_citations': ['Citation 1'],
            'conflicts': [],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Test Client')
        
        # Verify all required fields exist
        required_fields = [
            'client_name',
            'query_text',
            'ai_answer',
            'source_citations',
            'conflict_flag',
            'resolution_reasoning',
            'created_at'
        ]
        
        for field in required_fields:
            assert field in ticket_data
    
    def test_ticket_created_at_is_iso_format(self):
        """Test created_at field is in ISO format."""
        query_context = {
            'query_text': 'Test',
            'ai_answer': 'Test',
            'source_citations': [],
            'conflicts': [],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Client')
        
        # Verify created_at can be parsed as ISO datetime
        created_at = ticket_data['created_at']
        parsed_date = datetime.fromisoformat(created_at)
        assert isinstance(parsed_date, datetime)
    
    def test_ticket_preserves_citation_order(self):
        """Test ticket preserves order of source citations."""
        citations = [
            'Citation 1: First source',
            'Citation 2: Second source',
            'Citation 3: Third source'
        ]
        
        query_context = {
            'query_text': 'Test',
            'ai_answer': 'Test',
            'source_citations': citations,
            'conflicts': [],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Client')
        
        # Verify order is preserved
        assert ticket_data['source_citations'] == citations
        for i, citation in enumerate(citations):
            assert ticket_data['source_citations'][i] == citation


class TestEdgeCases:
    """Test edge cases for ticket creation."""
    
    def test_ticket_with_special_characters_in_query(self):
        """Test ticket creation with special characters in query text."""
        query_context = {
            'query_text': 'What is our policy for @#$%^&* characters?',
            'ai_answer': 'Special characters are handled properly.',
            'source_citations': [],
            'conflicts': [],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Client')
        assert ticket_data['query_text'] == 'What is our policy for @#$%^&* characters?'
    
    def test_ticket_with_unicode_characters(self):
        """Test ticket creation with unicode characters."""
        query_context = {
            'query_text': '¿Cuál es nuestra política de reembolso? 🎉',
            'ai_answer': 'La política permite devoluciones dentro de 60 días.',
            'source_citations': [],
            'conflicts': [],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Cliente Español')
        assert ticket_data['query_text'] == '¿Cuál es nuestra política de reembolso? 🎉'
        assert ticket_data['client_name'] == 'Cliente Español'
    
    def test_ticket_with_very_long_answer(self):
        """Test ticket creation with very long AI answer."""
        long_answer = 'A' * 10000
        
        query_context = {
            'query_text': 'Test',
            'ai_answer': long_answer,
            'source_citations': [],
            'conflicts': [],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, 'Client')
        assert ticket_data['ai_answer'] == long_answer
        assert len(ticket_data['ai_answer']) == 10000
    
    def test_ticket_with_empty_strings(self):
        """Test ticket creation with empty string values."""
        query_context = {
            'query_text': '',
            'ai_answer': '',
            'source_citations': [],
            'conflicts': [],
            'source_chunks': []
        }
        
        ticket_data = create_ticket_data(query_context, '')
        
        # Should still create ticket with empty values
        assert ticket_data['query_text'] == ''
        assert ticket_data['ai_answer'] == ''
        assert ticket_data['client_name'] == ''


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

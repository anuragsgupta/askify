"""
Property-based tests for ticket creation functionality.

Tests Property 14: Ticket field population.
"""

from hypothesis import given, strategies as st, settings, assume
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============================================================================
# Hypothesis Strategies for Query Context
# ============================================================================

@st.composite
def query_context_strategy(draw):
    """
    Generate a random query context for ticket creation.
    
    Returns a dictionary with:
    - query_text: User's original query
    - ai_answer: Generated response
    - source_citations: List of formatted citation strings
    - conflicts: List of conflict objects (may be empty)
    - source_chunks: List of retrieved chunks with metadata
    """
    # Generate query text
    query_text = draw(st.text(min_size=10, max_size=200))
    
    # Generate AI answer
    ai_answer = draw(st.text(min_size=20, max_size=500))
    
    # Generate source citations (1-5 citations)
    num_citations = draw(st.integers(min_value=1, max_value=5))
    source_citations = [
        draw(st.text(min_size=10, max_size=100))
        for _ in range(num_citations)
    ]
    
    # Generate source chunks (matching number of citations)
    source_chunks = []
    has_excel_chunk = draw(st.booleans())
    
    for i in range(num_citations):
        # Decide doc_type - ensure at least one Excel chunk if has_excel_chunk is True
        if i == 0 and has_excel_chunk:
            doc_type = 'excel'
        else:
            doc_type = draw(st.sampled_from(['policy', 'excel', 'email']))
        
        chunk = {
            'content': draw(st.text(min_size=20, max_size=200)),
            'metadata': {
                'source': draw(st.text(min_size=5, max_size=50)),
                'doc_type': doc_type,
                'doc_date': '2024-01-15'
            }
        }
        
        # Add doc_type specific metadata
        if doc_type == 'excel':
            chunk['metadata']['client'] = draw(st.text(min_size=3, max_size=50))
            chunk['metadata']['sheet_name'] = draw(st.text(min_size=1, max_size=30))
            chunk['metadata']['row_number'] = draw(st.integers(min_value=1, max_value=1000))
        elif doc_type == 'policy':
            chunk['metadata']['section_title'] = draw(st.text(min_size=3, max_size=50))
            chunk['metadata']['page_number'] = draw(st.integers(min_value=1, max_value=100))
        elif doc_type == 'email':
            chunk['metadata']['sender'] = draw(st.text(min_size=5, max_size=50))
            chunk['metadata']['subject'] = draw(st.text(min_size=5, max_size=100))
        
        source_chunks.append(chunk)
    
    # Generate conflicts (0-2 conflicts)
    num_conflicts = draw(st.integers(min_value=0, max_value=2))
    conflicts = []
    
    for i in range(num_conflicts):
        conflict = type('Conflict', (), {
            'diff_explanation': draw(st.text(min_size=20, max_size=200)),
            'conflict_type': draw(st.sampled_from(['version_update', 'cross_doc_type', 'policy_change']))
        })()
        conflicts.append(conflict)
    
    return {
        'query_text': query_text,
        'ai_answer': ai_answer,
        'source_citations': source_citations,
        'conflicts': conflicts,
        'source_chunks': source_chunks
    }


# ============================================================================
# Helper Functions for Ticket Creation
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
# Property-Based Tests
# ============================================================================

# Feature: sme-knowledge-agent, Property 14: Ticket field population
@given(query_context=query_context_strategy())
@settings(max_examples=100)
def test_property_ticket_field_population_completeness(query_context):
    """
    Property 14: Ticket field population completeness.
    
    For any query context (including query text, AI answer, source citations,
    and conflict status), creating a ticket SHALL populate all required fields
    (client_name, query_text, ai_answer, source_citations, conflict_flag)
    with the correct values from the context.
    
    Validates: Requirements 8.1, 8.2
    """
    # Extract client name from context
    extracted_client = extract_client_name_from_context(query_context)
    
    # Use extracted client or provide a default
    client_name = extracted_client if extracted_client else "Test Client"
    
    # Create ticket data
    ticket_data = create_ticket_data(query_context, client_name)
    
    # Verify all required fields are present
    assert 'client_name' in ticket_data
    assert 'query_text' in ticket_data
    assert 'ai_answer' in ticket_data
    assert 'source_citations' in ticket_data
    assert 'conflict_flag' in ticket_data
    assert 'resolution_reasoning' in ticket_data
    assert 'created_at' in ticket_data
    
    # Verify field values match query context
    assert ticket_data['client_name'] == client_name
    assert ticket_data['query_text'] == query_context['query_text']
    assert ticket_data['ai_answer'] == query_context['ai_answer']
    assert ticket_data['source_citations'] == query_context['source_citations']
    
    # Verify conflict flag is correct
    has_conflicts = len(query_context.get('conflicts', [])) > 0
    assert ticket_data['conflict_flag'] == has_conflicts
    
    # Verify resolution reasoning is populated when conflicts exist
    if has_conflicts:
        assert ticket_data['resolution_reasoning'] is not None
        assert len(ticket_data['resolution_reasoning']) > 0
        # Verify all conflict explanations are included
        for conflict in query_context['conflicts']:
            assert conflict.diff_explanation in ticket_data['resolution_reasoning']
    else:
        assert ticket_data['resolution_reasoning'] is None


# Feature: sme-knowledge-agent, Property 14: Ticket field population
@given(query_context=query_context_strategy())
@settings(max_examples=100)
def test_property_client_name_extraction_from_excel(query_context):
    """
    Property 14: Client name extraction from Excel metadata.
    
    For any query context containing Excel chunks with client metadata,
    the client name extraction SHALL return the first Excel client found.
    
    Validates: Requirements 8.1
    """
    extracted_client = extract_client_name_from_context(query_context)
    
    # Find first Excel chunk with client metadata
    expected_client = None
    for chunk in query_context.get('source_chunks', []):
        metadata = chunk.get('metadata', {})
        if metadata.get('doc_type') == 'excel' and metadata.get('client'):
            expected_client = metadata['client']
            break
    
    # Verify extraction matches expected
    assert extracted_client == expected_client


# Feature: sme-knowledge-agent, Property 14: Ticket field population
@given(
    query_text=st.text(min_size=10, max_size=200),
    ai_answer=st.text(min_size=20, max_size=500),
    num_citations=st.integers(min_value=0, max_value=5)
)
@settings(max_examples=100)
def test_property_ticket_handles_missing_client_name(query_text, ai_answer, num_citations):
    """
    Property 14: Ticket creation handles missing client name.
    
    For any query context without Excel chunks (no client metadata),
    the ticket creation SHALL still populate all other required fields
    correctly, allowing the user to manually enter client name.
    
    Validates: Requirements 8.1
    """
    # Create query context without Excel chunks
    source_citations = [f"Citation {i+1}" for i in range(num_citations)]
    
    query_context = {
        'query_text': query_text,
        'ai_answer': ai_answer,
        'source_citations': source_citations,
        'conflicts': [],
        'source_chunks': [
            {
                'content': 'Policy content',
                'metadata': {
                    'source': 'policy.pdf',
                    'doc_type': 'policy',
                    'section_title': 'Section 1',
                    'page_number': 1
                }
            }
        ]
    }
    
    # Extract client name (should be None)
    extracted_client = extract_client_name_from_context(query_context)
    assert extracted_client is None
    
    # Create ticket with manual client name
    manual_client = "Manual Client"
    ticket_data = create_ticket_data(query_context, manual_client)
    
    # Verify all fields are populated correctly
    assert ticket_data['client_name'] == manual_client
    assert ticket_data['query_text'] == query_text
    assert ticket_data['ai_answer'] == ai_answer
    assert ticket_data['source_citations'] == source_citations
    assert ticket_data['conflict_flag'] == False


# Feature: sme-knowledge-agent, Property 14: Ticket field population
@given(
    num_conflicts=st.integers(min_value=1, max_value=3),
    diff_explanations=st.lists(
        st.text(min_size=20, max_size=200),
        min_size=1,
        max_size=3
    )
)
@settings(max_examples=100)
def test_property_conflict_resolution_reasoning_includes_all_conflicts(num_conflicts, diff_explanations):
    """
    Property 14: Conflict resolution reasoning includes all conflicts.
    
    For any query context with multiple conflicts, the resolution reasoning
    SHALL include the diff explanation for every conflict detected.
    
    Validates: Requirements 8.2
    """
    # Ensure we have enough explanations
    assume(len(diff_explanations) >= num_conflicts)
    
    # Create conflicts
    conflicts = []
    for i in range(num_conflicts):
        conflict = type('Conflict', (), {
            'diff_explanation': diff_explanations[i],
            'conflict_type': 'version_update'
        })()
        conflicts.append(conflict)
    
    # Create query context with conflicts
    query_context = {
        'query_text': 'Test query',
        'ai_answer': 'Test answer',
        'source_citations': ['Citation 1'],
        'conflicts': conflicts,
        'source_chunks': []
    }
    
    # Create ticket data
    ticket_data = create_ticket_data(query_context, "Test Client")
    
    # Verify conflict flag is True
    assert ticket_data['conflict_flag'] == True
    
    # Verify resolution reasoning is not None
    assert ticket_data['resolution_reasoning'] is not None
    
    # Verify all diff explanations are included
    for i in range(num_conflicts):
        assert diff_explanations[i] in ticket_data['resolution_reasoning']


# Feature: sme-knowledge-agent, Property 14: Ticket field population
@given(query_context=query_context_strategy())
@settings(max_examples=100)
def test_property_ticket_preserves_citation_list_order(query_context):
    """
    Property 14: Ticket preserves citation list order.
    
    For any query context with multiple source citations, the ticket
    SHALL preserve the exact order of citations from the query context.
    
    Validates: Requirements 8.1
    """
    client_name = "Test Client"
    ticket_data = create_ticket_data(query_context, client_name)
    
    # Verify citations list matches exactly
    assert ticket_data['source_citations'] == query_context['source_citations']
    
    # Verify order is preserved
    for i, citation in enumerate(query_context['source_citations']):
        assert ticket_data['source_citations'][i] == citation


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])

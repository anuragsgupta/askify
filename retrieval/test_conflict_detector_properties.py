"""
Property-based tests for conflict detection middleware.

These tests validate universal correctness properties using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
import random

from retrieval.conflict_detector import (
    detect_conflicts,
    apply_date_priority_rule,
    generate_diff_explanation,
    flag_outdated_email,
    Conflict,
    _chunks_have_different_content
)


# Hypothesis strategies for generating test data

@st.composite
def chunk_metadata(draw, doc_type=None):
    """Generate random chunk metadata."""
    if doc_type is None:
        doc_type = draw(st.sampled_from(['policy', 'excel', 'email']))
    
    # Common metadata
    metadata = {
        'source': draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_.-'))),
        'doc_type': doc_type,
        'doc_date': draw(st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2024, 12, 31)
        )).isoformat()
    }
    
    # Doc-type specific metadata
    if doc_type == 'policy':
        metadata['section_title'] = draw(st.text(min_size=3, max_size=30))
        metadata['section_number'] = draw(st.text(min_size=1, max_size=10, alphabet='0123456789.'))
        metadata['page_number'] = draw(st.integers(min_value=1, max_value=100))
    elif doc_type == 'excel':
        metadata['sheet_name'] = draw(st.text(min_size=3, max_size=20))
        metadata['row_number'] = draw(st.integers(min_value=1, max_value=1000))
        metadata['client'] = draw(st.text(min_size=3, max_size=30))
    elif doc_type == 'email':
        metadata['sender'] = draw(st.emails())
        metadata['subject'] = draw(st.text(min_size=5, max_size=50))
        metadata['thread_id'] = draw(st.text(min_size=10, max_size=40))
        metadata['client_keyword'] = draw(st.text(min_size=3, max_size=20))
    
    return metadata


@st.composite
def document_chunk(draw, doc_type=None, metadata_override=None):
    """Generate random document chunk."""
    metadata = metadata_override if metadata_override else draw(chunk_metadata(doc_type=doc_type))
    
    chunk = {
        'content': draw(st.text(min_size=20, max_size=200)),
        'metadata': metadata,
        'score': draw(st.floats(min_value=0.0, max_value=1.0))
    }
    
    return chunk


@st.composite
def conflicting_chunk_pair(draw):
    """Generate a pair of chunks that should conflict."""
    doc_type = draw(st.sampled_from(['policy', 'excel', 'email']))
    
    # Create base metadata
    base_metadata = draw(chunk_metadata(doc_type=doc_type))
    
    # Create two dates that are different
    date1 = draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2023, 12, 31)))
    date2 = draw(st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2024, 12, 31)))
    
    # Ensure dates are different
    base_metadata['doc_date'] = date1.isoformat()
    newer_metadata = base_metadata.copy()
    newer_metadata['doc_date'] = date2.isoformat()
    newer_metadata['source'] = base_metadata['source'] + '_v2'
    
    # Create chunks with different content but same topic
    chunk1 = {
        'content': draw(st.text(min_size=20, max_size=100)) + " refund window is 30 days",
        'metadata': base_metadata,
        'score': 0.9
    }
    
    chunk2 = {
        'content': draw(st.text(min_size=20, max_size=100)) + " refund window is 60 days",
        'metadata': newer_metadata,
        'score': 0.85
    }
    
    return chunk1, chunk2


# Feature: sme-knowledge-agent, Property 11: Conflict detection and date-priority resolution
@settings(max_examples=100)
@given(conflicting_chunk_pair())
def test_property_conflict_detection_and_resolution(chunk_pair):
    """
    Property 11: For any pair of chunks that share the same topic,
    have different doc_dates, and have semantically different content,
    the conflict detector SHALL identify this as a conflict and select
    the chunk with the most recent doc_date as the winner.
    
    Validates: Requirements 6.1, 6.2
    """
    chunk1, chunk2 = chunk_pair
    chunks = [chunk1, chunk2]
    
    # Verify the chunks actually have different content
    # (the generator should ensure this, but let's verify)
    if not _chunks_have_different_content(chunk1, chunk2):
        # Skip this test case if content is too similar
        return
    
    # Detect conflicts
    conflicts = detect_conflicts(chunks)
    
    # Should detect at least one conflict
    assert len(conflicts) >= 1, "Should detect conflict between chunks with same topic but different dates and content"
    
    conflict = conflicts[0]
    
    # Verify winner has the most recent date
    winner_date = datetime.fromisoformat(conflict.winner['metadata']['doc_date'])
    
    for rejected_chunk in conflict.rejected:
        rejected_date = datetime.fromisoformat(rejected_chunk['metadata']['doc_date'])
        assert winner_date >= rejected_date, "Winner should have the most recent doc_date"
    
    # Verify conflict object structure
    assert isinstance(conflict, Conflict), "Should return Conflict object"
    assert conflict.winner is not None, "Conflict should have a winner"
    assert len(conflict.rejected) > 0, "Conflict should have rejected chunks"
    assert conflict.diff_explanation, "Conflict should have diff explanation"
    assert conflict.conflict_type in ['version_update', 'cross_doc_type', 'policy_change'], "Should have valid conflict type"


# Feature: sme-knowledge-agent, Property 11: Date priority rule application
@settings(max_examples=100)
@given(st.lists(document_chunk(), min_size=2, max_size=5))
def test_property_date_priority_rule(chunks):
    """
    Property 11 (continued): For any list of conflicting chunks,
    apply_date_priority_rule SHALL select the chunk with the most
    recent doc_date as the winner.
    
    Validates: Requirements 6.2
    """
    # Apply date priority rule
    winner, rejected = apply_date_priority_rule(chunks)
    
    # Verify winner has the most recent date
    winner_date = datetime.fromisoformat(winner['metadata']['doc_date'])
    
    for chunk in chunks:
        chunk_date = datetime.fromisoformat(chunk['metadata']['doc_date'])
        assert winner_date >= chunk_date, "Winner should have the most recent or equal doc_date"
    
    # Verify all chunks are accounted for
    assert len(rejected) == len(chunks) - 1, "Should have exactly one winner and rest rejected"
    
    # Verify winner is not in rejected list (by identity, not equality)
    winner_id = id(winner)
    rejected_ids = [id(r) for r in rejected]
    assert winner_id not in rejected_ids, "Winner should not be in rejected list"


# Feature: sme-knowledge-agent, Property 12: Diff explanation generation
@settings(max_examples=100)
@given(conflicting_chunk_pair())
def test_property_diff_explanation_generation(chunk_pair):
    """
    Property 12: For any detected conflict between two chunks,
    the system SHALL generate a non-empty diff explanation string
    that describes what changed between the older and newer versions.
    
    Validates: Requirements 6.3
    """
    chunk1, chunk2 = chunk_pair
    
    # Determine which is newer
    date1 = datetime.fromisoformat(chunk1['metadata']['doc_date'])
    date2 = datetime.fromisoformat(chunk2['metadata']['doc_date'])
    
    winner = chunk2 if date2 > date1 else chunk1
    rejected = chunk1 if date2 > date1 else chunk2
    
    # Generate diff explanation
    diff_explanation = generate_diff_explanation(winner, rejected)
    
    # Verify explanation is non-empty
    assert diff_explanation, "Diff explanation should not be empty"
    assert len(diff_explanation) > 10, "Diff explanation should be meaningful (>10 chars)"
    
    # Verify explanation contains source information
    assert winner['metadata']['source'] in diff_explanation or rejected['metadata']['source'] in diff_explanation, \
        "Diff explanation should reference source documents"
    
    # Verify explanation is a string
    assert isinstance(diff_explanation, str), "Diff explanation should be a string"


# Feature: sme-knowledge-agent, Property 13: Cross-doc-type outdated flagging
@settings(max_examples=100)
@given(
    email_chunk=document_chunk(doc_type='email'),
    pdf_chunk=document_chunk(doc_type='policy')
)
def test_property_cross_doc_type_outdated_flagging(email_chunk, pdf_chunk):
    """
    Property 13: For any email chunk and PDF chunk that share the same topic,
    if the email's doc_date is earlier than the PDF's doc_date,
    the system SHALL flag the email as containing outdated advice.
    
    Validates: Requirements 6.4
    """
    # Make them share a topic by setting same section_title/client_keyword
    topic = "Refund Policy"
    email_chunk['metadata']['client_keyword'] = topic
    pdf_chunk['metadata']['section_title'] = topic
    
    # Set dates so email predates PDF
    email_date = datetime(2023, 1, 1)
    pdf_date = datetime(2024, 1, 1)
    
    email_chunk['metadata']['doc_date'] = email_date.isoformat()
    pdf_chunk['metadata']['doc_date'] = pdf_date.isoformat()
    
    # Flag outdated email
    is_outdated = flag_outdated_email(email_chunk, pdf_chunk)
    
    # Should flag as outdated since email predates PDF
    assert is_outdated, "Email should be flagged as outdated when it predates PDF on same topic"
    
    # Test reverse: PDF predates email (should not flag)
    email_chunk['metadata']['doc_date'] = pdf_date.isoformat()
    pdf_chunk['metadata']['doc_date'] = email_date.isoformat()
    
    is_outdated_reverse = flag_outdated_email(email_chunk, pdf_chunk)
    assert not is_outdated_reverse, "Email should not be flagged when it's newer than PDF"


# Feature: sme-knowledge-agent, Property 13: Outdated flagging requires topic match
@settings(max_examples=100)
@given(
    email_chunk=document_chunk(doc_type='email'),
    pdf_chunk=document_chunk(doc_type='policy')
)
def test_property_outdated_flagging_requires_topic_match(email_chunk, pdf_chunk):
    """
    Property 13 (continued): Outdated flagging should only occur
    when email and PDF share the same topic.
    
    Validates: Requirements 6.4
    """
    # Ensure they DON'T share a topic
    email_chunk['metadata']['client_keyword'] = "Topic A"
    pdf_chunk['metadata']['section_title'] = "Topic B"
    
    # Set dates so email predates PDF
    email_date = datetime(2023, 1, 1)
    pdf_date = datetime(2024, 1, 1)
    
    email_chunk['metadata']['doc_date'] = email_date.isoformat()
    pdf_chunk['metadata']['doc_date'] = pdf_date.isoformat()
    
    # Flag outdated email
    is_outdated = flag_outdated_email(email_chunk, pdf_chunk)
    
    # Should NOT flag as outdated since topics don't match
    assert not is_outdated, "Email should not be flagged when topics don't match"


# Feature: sme-knowledge-agent, Property 11: No conflicts when dates are same
@settings(max_examples=100)
@given(document_chunk())
def test_property_no_conflict_same_date(base_chunk):
    """
    Property 11 (edge case): Chunks with the same date should not
    be flagged as conflicts even if content differs slightly.
    
    Validates: Requirements 6.1
    """
    # Create two chunks with same date and topic but slightly different content
    chunk1 = base_chunk.copy()
    chunk2 = base_chunk.copy()
    chunk2['content'] = chunk1['content'] + " additional text"
    
    chunks = [chunk1, chunk2]
    
    # Detect conflicts
    conflicts = detect_conflicts(chunks)
    
    # Should not detect conflicts when dates are the same
    # (even if content differs, same date means same version)
    assert len(conflicts) == 0, "Should not detect conflicts when doc_dates are identical"


# Feature: sme-knowledge-agent, Property 11: No conflicts when topics differ
@settings(max_examples=100)
@given(
    chunk1=document_chunk(doc_type='policy'),
    chunk2=document_chunk(doc_type='policy')
)
def test_property_no_conflict_different_topics(chunk1, chunk2):
    """
    Property 11 (edge case): Chunks with different topics should not
    be flagged as conflicts even if dates differ.
    
    Validates: Requirements 6.1
    """
    # Ensure different topics
    chunk1['metadata']['section_title'] = "Refund Policy"
    chunk2['metadata']['section_title'] = "Shipping Policy"
    
    # Ensure different dates
    chunk1['metadata']['doc_date'] = datetime(2023, 1, 1).isoformat()
    chunk2['metadata']['doc_date'] = datetime(2024, 1, 1).isoformat()
    
    chunks = [chunk1, chunk2]
    
    # Detect conflicts
    conflicts = detect_conflicts(chunks)
    
    # Should not detect conflicts when topics are different
    assert len(conflicts) == 0, "Should not detect conflicts when topics differ"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

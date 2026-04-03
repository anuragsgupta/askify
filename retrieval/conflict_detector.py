"""
Conflict detection middleware for SME Knowledge Agent.

This module analyzes retrieved chunks for contradictions and applies
date-priority resolution rules to ensure employees receive the most
current information.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import re


@dataclass
class Conflict:
    """Represents a detected conflict between document chunks."""
    winner: Dict[str, Any]
    rejected: List[Dict[str, Any]]
    diff_explanation: str
    conflict_type: str  # "version_update" | "cross_doc_type" | "policy_change"


def detect_conflicts(chunks: List[Dict[str, Any]]) -> List[Conflict]:
    """
    Analyzes retrieved chunks for contradictions.
    
    Conflict criteria:
    - Same section_title (for PDFs) or same client (for Excel/email)
    - Different doc_dates
    - Different content (semantic similarity < 0.9)
    
    Args:
        chunks: List of retrieved chunks with content and metadata
        
    Returns:
        List of Conflict objects with winner, rejected chunks, and explanations
    """
    if not chunks or len(chunks) < 2:
        return []
    
    conflicts = []
    processed_indices = set()
    
    # Group chunks by topic (section_title or client)
    for i, chunk1 in enumerate(chunks):
        if i in processed_indices:
            continue
            
        conflicting_group = [chunk1]
        
        for j, chunk2 in enumerate(chunks[i+1:], start=i+1):
            if j in processed_indices:
                continue
                
            # Check if chunks share the same topic
            if _chunks_share_topic(chunk1, chunk2):
                # Check if they have different dates
                if _chunks_have_different_dates(chunk1, chunk2):
                    # Check if content is semantically different
                    if _chunks_have_different_content(chunk1, chunk2):
                        conflicting_group.append(chunk2)
                        processed_indices.add(j)
        
        # If we found conflicts, resolve them
        if len(conflicting_group) > 1:
            processed_indices.add(i)
            winner, rejected = apply_date_priority_rule(conflicting_group)
            
            # Generate diff explanation for each rejected chunk
            diff_explanation = generate_diff_explanation(winner, rejected[0] if rejected else winner)
            
            # Determine conflict type
            conflict_type = _determine_conflict_type(winner, rejected)
            
            conflicts.append(Conflict(
                winner=winner,
                rejected=rejected,
                diff_explanation=diff_explanation,
                conflict_type=conflict_type
            ))
    
    return conflicts


def apply_date_priority_rule(conflicting_chunks: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Selects chunk with most recent doc_date as winner.
    
    Args:
        conflicting_chunks: List of chunks that conflict with each other
        
    Returns:
        Tuple of (winner, list of rejected chunks)
    """
    if not conflicting_chunks:
        raise ValueError("Cannot apply date priority rule to empty list")
    
    if len(conflicting_chunks) == 1:
        return conflicting_chunks[0], []
    
    # Sort by doc_date (most recent first)
    sorted_chunks = sorted(
        conflicting_chunks,
        key=lambda c: _parse_doc_date(c.get('metadata', {}).get('doc_date', '')),
        reverse=True
    )
    
    winner = sorted_chunks[0]
    rejected = sorted_chunks[1:]
    
    return winner, rejected


def generate_diff_explanation(winner: Dict[str, Any], rejected: Dict[str, Any]) -> str:
    """
    Generates plain-language diff explanation between winner and rejected chunk.
    
    Compares content and metadata to describe what changed.
    Example: "Refund window changed from 30 days (Policy v1, 2023-01-15) to 60 days (Policy v2, 2024-03-01)"
    
    Args:
        winner: The winning chunk (most recent)
        rejected: The rejected chunk (older)
        
    Returns:
        Plain-language description of changes
    """
    winner_meta = winner.get('metadata', {})
    rejected_meta = rejected.get('metadata', {})
    
    winner_content = winner.get('content', '')
    rejected_content = rejected.get('content', '')
    
    # Extract key information
    winner_source = winner_meta.get('source', 'Unknown')
    rejected_source = rejected_meta.get('source', 'Unknown')
    winner_date = winner_meta.get('doc_date', 'Unknown date')
    rejected_date = rejected_meta.get('doc_date', 'Unknown date')
    
    # Try to identify specific changes using simple heuristics
    # Look for numbers that changed
    winner_numbers = re.findall(r'\d+', winner_content)
    rejected_numbers = re.findall(r'\d+', rejected_content)
    
    # Build explanation
    explanation_parts = []
    
    # Identify the topic
    topic = winner_meta.get('section_title') or winner_meta.get('client') or 'content'
    
    # Check for number changes (common in policy updates)
    if winner_numbers and rejected_numbers:
        # Find numbers that appear in one but not the other
        unique_to_rejected = set(rejected_numbers) - set(winner_numbers)
        unique_to_winner = set(winner_numbers) - set(rejected_numbers)
        
        if unique_to_rejected and unique_to_winner:
            explanation_parts.append(
                f"Values changed from {', '.join(sorted(unique_to_rejected))} "
                f"to {', '.join(sorted(unique_to_winner))}"
            )
    
    # Add source and date information
    explanation_parts.append(
        f"Updated from {rejected_source} ({_format_date(rejected_date)}) "
        f"to {winner_source} ({_format_date(winner_date)})"
    )
    
    # Combine parts
    if len(explanation_parts) > 1:
        explanation = f"{topic}: {explanation_parts[0]}. {explanation_parts[1]}."
    else:
        explanation = f"{topic}: {explanation_parts[0]}."
    
    return explanation


def flag_outdated_email(email_chunk: Dict[str, Any], pdf_chunk: Dict[str, Any]) -> bool:
    """
    Checks if email chunk predates PDF chunk on same topic.
    
    Topic matching uses section_title or client field.
    
    Args:
        email_chunk: Email chunk with metadata
        pdf_chunk: PDF chunk with metadata
        
    Returns:
        True if email contains outdated advice (predates PDF)
    """
    email_meta = email_chunk.get('metadata', {})
    pdf_meta = pdf_chunk.get('metadata', {})
    
    # Verify this is actually an email and PDF
    if email_meta.get('doc_type') != 'email':
        return False
    if pdf_meta.get('doc_type') != 'policy':
        return False
    
    # Check if they share a topic
    if not _chunks_share_topic(email_chunk, pdf_chunk):
        return False
    
    # Compare dates
    email_date = _parse_doc_date(email_meta.get('doc_date', ''))
    pdf_date = _parse_doc_date(pdf_meta.get('doc_date', ''))
    
    # Email is outdated if it predates the PDF
    return email_date < pdf_date


# Helper functions

def _chunks_share_topic(chunk1: Dict[str, Any], chunk2: Dict[str, Any]) -> bool:
    """
    Checks if two chunks share the same topic.
    
    Topics are matched by:
    - section_title (for PDFs)
    - client (for Excel/email)
    - subject keywords (for emails)
    - Cross-doc-type matching (e.g., email client_keyword vs PDF section_title)
    """
    meta1 = chunk1.get('metadata', {})
    meta2 = chunk2.get('metadata', {})
    
    # Check section_title match (case-insensitive)
    section1 = meta1.get('section_title', '').lower().strip()
    section2 = meta2.get('section_title', '').lower().strip()
    if section1 and section2 and section1 == section2:
        return True
    
    # Check client match (case-insensitive)
    client1 = meta1.get('client', '').lower().strip()
    client2 = meta2.get('client', '').lower().strip()
    if client1 and client2 and client1 == client2:
        return True
    
    # Check client_keyword match (for emails)
    keyword1 = meta1.get('client_keyword', '').lower().strip()
    keyword2 = meta2.get('client_keyword', '').lower().strip()
    if keyword1 and keyword2 and keyword1 == keyword2:
        return True
    
    # Cross-doc-type matching: email client_keyword vs PDF section_title
    if keyword1 and section2 and keyword1 == section2:
        return True
    if keyword2 and section1 and keyword2 == section1:
        return True
    
    # Check if subject lines share significant keywords (for emails)
    subject1 = meta1.get('subject', '').lower()
    subject2 = meta2.get('subject', '').lower()
    if subject1 and subject2:
        # Extract significant words (3+ characters)
        words1 = set(w for w in re.findall(r'\b\w{3,}\b', subject1))
        words2 = set(w for w in re.findall(r'\b\w{3,}\b', subject2))
        # If they share 2+ significant words, consider them related
        if len(words1 & words2) >= 2:
            return True
    
    # Check if email subject contains PDF section title or vice versa
    if subject1 and section2:
        # Extract significant words from section title
        section_words = set(w for w in re.findall(r'\b\w{3,}\b', section2))
        subject_words = set(w for w in re.findall(r'\b\w{3,}\b', subject1))
        if len(section_words & subject_words) >= 2:
            return True
    
    if subject2 and section1:
        section_words = set(w for w in re.findall(r'\b\w{3,}\b', section1))
        subject_words = set(w for w in re.findall(r'\b\w{3,}\b', subject2))
        if len(section_words & subject_words) >= 2:
            return True
    
    return False


def _chunks_have_different_dates(chunk1: Dict[str, Any], chunk2: Dict[str, Any]) -> bool:
    """Checks if two chunks have different doc_dates."""
    date1 = chunk1.get('metadata', {}).get('doc_date', '')
    date2 = chunk2.get('metadata', {}).get('doc_date', '')
    
    if not date1 or not date2:
        return False
    
    # Parse and compare dates
    parsed_date1 = _parse_doc_date(date1)
    parsed_date2 = _parse_doc_date(date2)
    
    return parsed_date1 != parsed_date2


def _chunks_have_different_content(chunk1: Dict[str, Any], chunk2: Dict[str, Any], threshold: float = 0.85) -> bool:
    """
    Checks if two chunks have semantically different content.
    
    Uses simple similarity metric based on word overlap.
    For production, could use sentence embeddings for better accuracy.
    
    Args:
        chunk1: First chunk
        chunk2: Second chunk
        threshold: Similarity threshold (default 0.85, below this = different)
        
    Returns:
        True if content is different (similarity < threshold)
    """
    content1 = chunk1.get('content', '').lower()
    content2 = chunk2.get('content', '').lower()
    
    if not content1 or not content2:
        return False
    
    # Simple word-based similarity (Jaccard similarity)
    words1 = set(re.findall(r'\b\w+\b', content1))
    words2 = set(re.findall(r'\b\w+\b', content2))
    
    if not words1 or not words2:
        return False
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    similarity = intersection / union if union > 0 else 0.0
    
    return similarity < threshold


def _parse_doc_date(date_str: str) -> datetime:
    """
    Parses doc_date string to datetime object.
    
    Handles ISO format and common date formats.
    Returns epoch (1970-01-01) if parsing fails.
    All returned datetimes are timezone-naive for consistent comparison.
    """
    if not date_str:
        return datetime(1970, 1, 1)
    
    # Try ISO format first
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # Convert to naive datetime for consistent comparison
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt
    except (ValueError, AttributeError):
        pass
    
    # Try common formats
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d',
        '%m/%d/%Y',
        '%d/%m/%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    
    # Return epoch if all parsing fails
    return datetime(1970, 1, 1)


def _format_date(date_str: str) -> str:
    """Formats date string for display."""
    parsed = _parse_doc_date(date_str)
    if parsed.year == 1970:
        return date_str  # Return original if parsing failed
    return parsed.strftime('%Y-%m-%d')


def _determine_conflict_type(winner: Dict[str, Any], rejected: List[Dict[str, Any]]) -> str:
    """
    Determines the type of conflict based on metadata.
    
    Returns:
        "version_update" - same doc type, different versions
        "cross_doc_type" - different doc types (e.g., email vs PDF)
        "policy_change" - policy document updates
    """
    if not rejected:
        return "policy_change"
    
    winner_type = winner.get('metadata', {}).get('doc_type', '')
    rejected_type = rejected[0].get('metadata', {}).get('doc_type', '')
    
    # Cross-doc-type conflict
    if winner_type != rejected_type:
        return "cross_doc_type"
    
    # Policy version update
    if winner_type == 'policy':
        winner_source = winner.get('metadata', {}).get('source', '')
        rejected_source = rejected[0].get('metadata', {}).get('source', '')
        
        # Check for version indicators in filename
        if re.search(r'v\d+|version', winner_source, re.I) or re.search(r'v\d+|version', rejected_source, re.I):
            return "version_update"
        
        return "policy_change"
    
    # Default to version update
    return "version_update"

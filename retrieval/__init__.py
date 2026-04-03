"""Retrieval layer for SME Knowledge Agent."""

from retrieval.conflict_detector import (
    Conflict,
    detect_conflicts,
    apply_date_priority_rule,
    generate_diff_explanation,
    flag_outdated_email
)

from retrieval.query_engine import (
    QueryResult,
    create_query_engine,
    query_with_metadata,
    retrieve_chunks
)

__all__ = [
    # Conflict detection
    'Conflict',
    'detect_conflicts',
    'apply_date_priority_rule',
    'generate_diff_explanation',
    'flag_outdated_email',
    
    # Query engine
    'QueryResult',
    'create_query_engine',
    'query_with_metadata',
    'retrieve_chunks',
]

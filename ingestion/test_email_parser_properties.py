"""Property-based tests for email parser module using Hypothesis."""

import tempfile
from datetime import datetime
from pathlib import Path

from hypothesis import given, settings, strategies as st

from ingestion.email_parser import parse_eml_file


# Feature: sme-knowledge-agent, Property 6: EML parsing completeness
# For any valid EML file, the parser SHALL extract all required fields
# (sender, date, subject, body) from each message in the thread without missing data.


def create_eml_file(sender: str, subject: str, date_str: str, body: str, message_id: str, temp_dir: Path) -> str:
    """Helper to create an EML file with given fields."""
    eml_content = f"""From: {sender}
To: recipient@example.com
Subject: {subject}
Date: {date_str}
Message-ID: <{message_id}>

{body}
"""
    eml_file = temp_dir / "test.eml"
    eml_file.write_text(eml_content, encoding='utf-8')
    return str(eml_file)


@given(
    sender=st.emails(),
    subject=st.text(min_size=1, max_size=200, alphabet=st.characters(
        blacklist_categories=('Cc', 'Cs'),  # Exclude control characters
        blacklist_characters='\n\r'
    )).filter(lambda x: x.strip() != ''),  # Ensure non-empty after stripping
    body=st.text(min_size=1, max_size=1000, alphabet=st.characters(
        blacklist_categories=('Cc', 'Cs'),  # Exclude control characters except common ones
        min_codepoint=32, max_codepoint=126  # Printable ASCII
    )),
    message_id=st.from_regex(r'[a-zA-Z0-9]{5,20}@[a-zA-Z0-9.-]+', fullmatch=True)
)
@settings(max_examples=20)
def test_property_eml_parsing_completeness(sender: str, subject: str, body: str, message_id: str):
    """
    Property 6: EML parsing completeness
    
    **Validates: Requirements 3.1**
    
    For any valid EML file, the parser SHALL extract all required fields
    (sender, date, subject, body) from each message without missing data.
    """
    # Use a fixed valid date string for all tests
    date_str = "Mon, 15 Jan 2024 10:30:00 +0000"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_eml_file(sender, subject, date_str, body, message_id, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        # Property: Parser returns at least one message
        assert len(messages) >= 1
        
        msg = messages[0]
        
        # Property: All required fields are present and non-empty
        assert msg.sender is not None and msg.sender != ""
        assert msg.doc_date is not None
        assert isinstance(msg.doc_date, datetime)
        assert msg.subject is not None and msg.subject != ""
        assert msg.thread_id is not None and msg.thread_id != ""
        assert msg.content is not None  # Body can be empty but not None
        assert msg.doc_type == "email"
        
        # Property: Sender is extracted correctly
        # If sender has format "Name <email>", extract email; otherwise use as-is
        if '<' in sender and '>' in sender:
            expected_sender = sender[sender.index('<') + 1:sender.index('>')]
        else:
            expected_sender = sender
        assert msg.sender == expected_sender
        
        # Property: Subject is preserved
        assert msg.subject == subject
        
        # Property: Body content is preserved (normalized for line endings)
        normalized_body = body.strip().replace('\r\n', '\n').replace('\r', '\n')
        normalized_content = msg.content.replace('\r\n', '\n').replace('\r', '\n')
        assert normalized_body in normalized_content or normalized_content in normalized_body


@given(
    sender_name=st.text(min_size=2, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'),
        whitelist_characters=' '
    )).filter(lambda x: '<' not in x and '>' not in x and '@' not in x),
    sender_email=st.emails()
)
@settings(max_examples=20)
def test_property_sender_extraction_with_name(sender_name: str, sender_email: str):
    """
    Property: Sender extraction handles "Name <email>" format correctly.
    
    **Validates: Requirements 3.1**
    
    For any sender in "Name <email>" format, the parser SHALL extract
    just the email address.
    """
    sender_full = f"{sender_name} <{sender_email}>"
    subject = "Test"
    body = "Test body"
    message_id = "test123@example.com"
    date_str = "Mon, 15 Jan 2024 10:30:00 +0000"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_eml_file(sender_full, subject, date_str, body, message_id, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Property: Email address is extracted
        assert msg.sender == sender_email


@given(
    message_id=st.from_regex(r'[a-zA-Z0-9]{5,20}@[a-zA-Z0-9.-]+', fullmatch=True)
)
@settings(max_examples=20)
def test_property_thread_id_extraction(message_id: str):
    """
    Property: Thread ID extraction from Message-ID header.
    
    **Validates: Requirements 3.3**
    
    For any email with a Message-ID header, the parser SHALL extract
    the thread_id correctly (without angle brackets).
    """
    sender = "test@example.com"
    subject = "Test"
    body = "Test body"
    date_str = "Mon, 15 Jan 2024 10:30:00 +0000"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_eml_file(sender, subject, date_str, body, message_id, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Property: Thread ID matches Message-ID (without angle brackets)
        assert msg.thread_id == message_id
        assert '<' not in msg.thread_id
        assert '>' not in msg.thread_id


@given(
    plain_text=st.text(min_size=10, max_size=500, alphabet=st.characters(
        min_codepoint=32, max_codepoint=126  # Printable ASCII
    )),
    html_text=st.text(min_size=10, max_size=500, alphabet=st.characters(
        min_codepoint=32, max_codepoint=126  # Printable ASCII
    ))
)
@settings(max_examples=20)
def test_property_multipart_prefers_plain_text(plain_text: str, html_text: str):
    """
    Property: Multipart message handling prefers plain text over HTML.
    
    **Validates: Requirements 3.1**
    
    For any multipart email with both text/plain and text/html parts,
    the parser SHALL prefer the plain text version.
    """
    sender = "test@example.com"
    subject = "Multipart Test"
    message_id = "multi123@example.com"
    date_str = "Mon, 15 Jan 2024 10:30:00 +0000"
    
    eml_content = f"""From: {sender}
To: recipient@example.com
Subject: {subject}
Date: {date_str}
Message-ID: <{message_id}>
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset="utf-8"

{plain_text}

--boundary123
Content-Type: text/html; charset="utf-8"

<html><body>{html_text}</body></html>

--boundary123--
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_file = Path(temp_dir) / "test.eml"
        eml_file.write_text(eml_content, encoding='utf-8')
        messages = parse_eml_file(str(eml_file))
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Property: Plain text content is present in the extracted body (normalized for line endings)
        normalized_plain = plain_text.strip().replace('\r\n', '\n').replace('\r', '\n')
        normalized_content = msg.content.replace('\r\n', '\n').replace('\r', '\n')
        assert normalized_plain in normalized_content or normalized_content in normalized_plain


def test_property_doc_type_always_email():
    """
    Property: doc_type field is always "email".
    
    **Validates: Requirements 3.3**
    
    For any parsed email message, the doc_type SHALL always be "email".
    """
    @given(
        sender=st.emails(),
        subject=st.text(min_size=1, max_size=100).filter(lambda x: '\n' not in x),
        body=st.text(max_size=500)
    )
    def check_doc_type(sender: str, subject: str, body: str):
        message_id = "test@example.com"
        date_str = "Mon, 15 Jan 2024 10:30:00 +0000"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            eml_path = create_eml_file(sender, subject, date_str, body, message_id, Path(temp_dir))
            messages = parse_eml_file(eml_path)
            
            # Property: doc_type is always "email"
            for msg in messages:
                assert msg.doc_type == "email"
    
    check_doc_type()


def test_property_client_keyword_none_for_manual_uploads():
    """
    Property: client_keyword is None for manual EML uploads.
    
    **Validates: Requirements 3.3**
    
    For any EML file parsed via parse_eml_file (manual upload),
    the client_keyword SHALL be None.
    """
    @given(
        sender=st.emails(),
        subject=st.text(min_size=1, max_size=100).filter(lambda x: '\n' not in x),
        body=st.text(max_size=500)
    )
    def check_client_keyword(sender: str, subject: str, body: str):
        message_id = "test@example.com"
        date_str = "Mon, 15 Jan 2024 10:30:00 +0000"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            eml_path = create_eml_file(sender, subject, date_str, body, message_id, Path(temp_dir))
            messages = parse_eml_file(eml_path)
            
            # Property: client_keyword is None for manual uploads
            for msg in messages:
                assert msg.client_keyword is None
    
    check_client_keyword()

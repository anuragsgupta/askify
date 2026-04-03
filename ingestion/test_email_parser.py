"""Unit tests for email parser module."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ingestion.email_parser import (
    EmailMessage,
    extract_body,
    extract_thread_id,
    parse_eml_file,
)


def create_test_eml(content: str, temp_dir: Path) -> str:
    """Helper to create a temporary EML file for testing."""
    eml_file = temp_dir / "test_email.eml"
    eml_file.write_text(content)
    return str(eml_file)


def test_parse_simple_email():
    """Test parsing a simple plain text email."""
    eml_content = """From: john@example.com
To: jane@example.com
Subject: Test Email
Date: Mon, 15 Jan 2024 10:30:00 +0000
Message-ID: <abc123@example.com>

This is a test email body.
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_test_eml(eml_content, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        assert msg.sender == "john@example.com"
        assert msg.subject == "Test Email"
        assert msg.thread_id == "abc123@example.com"
        assert msg.doc_type == "email"
        assert msg.client_keyword is None
        assert "test email body" in msg.content.lower()


def test_parse_email_with_name_in_sender():
    """Test parsing email where sender has name and email format."""
    eml_content = """From: John Doe <john@example.com>
To: jane@example.com
Subject: Meeting Request
Date: Mon, 15 Jan 2024 10:30:00 +0000
Message-ID: <xyz789@example.com>

Let's schedule a meeting.
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_test_eml(eml_content, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Should extract just the email address
        assert msg.sender == "john@example.com"
        assert msg.subject == "Meeting Request"


def test_parse_multipart_email_plain_text():
    """Test parsing multipart email with plain text part."""
    eml_content = """From: sender@example.com
To: recipient@example.com
Subject: Multipart Test
Date: Mon, 15 Jan 2024 10:30:00 +0000
Message-ID: <multi123@example.com>
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset="utf-8"

This is the plain text version.

--boundary123
Content-Type: text/html; charset="utf-8"

<html><body>This is the HTML version.</body></html>

--boundary123--
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_test_eml(eml_content, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Should prefer plain text over HTML
        assert "plain text version" in msg.content.lower()
        assert "html version" not in msg.content.lower()


def test_parse_email_missing_message_id():
    """Test parsing email without Message-ID (uses References fallback)."""
    eml_content = """From: sender@example.com
To: recipient@example.com
Subject: Reply Email
Date: Mon, 15 Jan 2024 10:30:00 +0000
References: <original123@example.com> <reply456@example.com>

This is a reply.
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_test_eml(eml_content, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Should use first reference as thread_id
        assert msg.thread_id == "original123@example.com"


def test_parse_email_missing_date():
    """Test parsing email without Date header (uses file mtime)."""
    eml_content = """From: sender@example.com
To: recipient@example.com
Subject: No Date Email
Message-ID: <nodate123@example.com>

Email without date header.
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_test_eml(eml_content, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Should have a valid datetime (from file mtime)
        assert isinstance(msg.doc_date, datetime)


def test_parse_email_missing_subject():
    """Test parsing email without Subject header."""
    eml_content = """From: sender@example.com
To: recipient@example.com
Date: Mon, 15 Jan 2024 10:30:00 +0000
Message-ID: <nosub123@example.com>

Email without subject.
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_test_eml(eml_content, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Should have default subject
        assert msg.subject == "No Subject"


def test_parse_email_with_in_reply_to():
    """Test parsing email with In-Reply-To header for thread_id."""
    eml_content = """From: sender@example.com
To: recipient@example.com
Subject: Re: Original Subject
Date: Mon, 15 Jan 2024 10:30:00 +0000
In-Reply-To: <original999@example.com>

This is a reply using In-Reply-To.
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_test_eml(eml_content, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Should use In-Reply-To as thread_id
        assert msg.thread_id == "original999@example.com"


def test_parse_email_missing_sender():
    """Test parsing email without From header (uses default)."""
    eml_content = """To: recipient@example.com
Subject: No Sender Email
Date: Mon, 15 Jan 2024 10:30:00 +0000
Message-ID: <nosender123@example.com>

Email without sender.
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_test_eml(eml_content, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Should have default sender
        assert msg.sender == "unknown@unknown.com"


def test_parse_malformed_eml_file():
    """Test parsing malformed EML file (invalid structure)."""
    eml_content = """This is not a valid EML file
Just some random text
Without proper headers
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_test_eml(eml_content, Path(temp_dir))
        
        # Should not raise exception, but parse what it can
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Should have default values for missing fields
        assert msg.sender == "unknown@unknown.com"
        assert msg.subject == "No Subject"
        assert isinstance(msg.doc_date, datetime)


def test_parse_multipart_with_attachments():
    """Test parsing multipart email with attachments (attachments should be skipped)."""
    eml_content = """From: sender@example.com
To: recipient@example.com
Subject: Email with Attachment
Date: Mon, 15 Jan 2024 10:30:00 +0000
Message-ID: <attach123@example.com>
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary456"

--boundary456
Content-Type: text/plain; charset="utf-8"

This is the email body with an attachment.

--boundary456
Content-Type: application/pdf; name="document.pdf"
Content-Disposition: attachment; filename="document.pdf"
Content-Transfer-Encoding: base64

JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRv
YmoKMiAwIG9iago8PC9UeXBlL1BhZ2VzL0NvdW50IDEvS2lkc1szIDAgUl0+PgplbmRvYmoKMyAw
IG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3hbMCAwIDYxMiA3OTJdL1BhcmVudCAyIDAgUi9SZXNv

--boundary456--
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        eml_path = create_test_eml(eml_content, Path(temp_dir))
        messages = parse_eml_file(eml_path)
        
        assert len(messages) == 1
        msg = messages[0]
        
        # Should extract body text but skip attachment
        assert "email body with an attachment" in msg.content.lower()
        # Should not contain base64 encoded attachment data
        assert "JVBERi0xLjQK" not in msg.content


def test_email_message_dataclass():
    """Test EmailMessage dataclass structure."""
    msg = EmailMessage(
        sender="test@example.com",
        doc_date=datetime(2024, 1, 15, 10, 30),
        subject="Test Subject",
        thread_id="thread123",
        client_keyword="Acme Corp",
        doc_type="email",
        content="Test content"
    )
    
    assert msg.sender == "test@example.com"
    assert msg.doc_date == datetime(2024, 1, 15, 10, 30)
    assert msg.subject == "Test Subject"
    assert msg.thread_id == "thread123"
    assert msg.client_keyword == "Acme Corp"
    assert msg.doc_type == "email"
    assert msg.content == "Test content"

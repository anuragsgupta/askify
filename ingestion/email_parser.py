"""Email parsing module for extracting messages from EML files."""

import email
from dataclasses import dataclass
from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class EmailMessage:
    """Represents a parsed email message with metadata."""
    sender: str
    doc_date: datetime
    subject: str
    thread_id: str
    client_keyword: Optional[str]
    doc_type: str
    content: str


def extract_thread_id(msg: email.message.EmailMessage) -> str:
    """
    Extracts thread identifier from email headers.
    
    Tries Message-ID first, then References header, then In-Reply-To.
    
    Args:
        msg: Parsed email message object
        
    Returns:
        Thread ID string (Message-ID or first reference)
    """
    # Try Message-ID first (most reliable)
    message_id = msg.get('Message-ID')
    if message_id:
        return message_id.strip('<>')
    
    # Try References header (contains thread history)
    references = msg.get('References')
    if references:
        # References contains space-separated message IDs
        ref_ids = references.split()
        if ref_ids:
            return ref_ids[0].strip('<>')
    
    # Try In-Reply-To header
    in_reply_to = msg.get('In-Reply-To')
    if in_reply_to:
        return in_reply_to.strip('<>')
    
    # Fallback: use subject as thread identifier
    subject = msg.get('Subject', 'no-subject')
    return f"thread-{hash(subject)}"


def extract_body(msg: email.message.EmailMessage) -> str:
    """
    Extracts email body, preferring plain text over HTML.
    
    Handles multipart messages by walking through parts.
    
    Args:
        msg: Parsed email message object
        
    Returns:
        Email body text (plain text preferred)
    """
    body = ""
    
    if msg.is_multipart():
        # Walk through message parts
        plain_text_parts = []
        html_parts = []
        
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition', ''))
            
            # Skip attachments
            if 'attachment' in content_disposition:
                continue
            
            if content_type == 'text/plain':
                try:
                    plain_text_parts.append(part.get_content())
                except Exception:
                    # Handle decoding errors gracefully
                    continue
            elif content_type == 'text/html':
                try:
                    html_parts.append(part.get_content())
                except Exception:
                    continue
        
        # Prefer plain text over HTML
        if plain_text_parts:
            body = '\n'.join(plain_text_parts)
        elif html_parts:
            # Basic HTML stripping (remove tags)
            import re
            html_body = '\n'.join(html_parts)
            body = re.sub(r'<[^>]+>', '', html_body)
    else:
        # Single part message
        content_type = msg.get_content_type()
        if content_type == 'text/plain':
            try:
                body = msg.get_content()
            except Exception:
                body = ""
        elif content_type == 'text/html':
            # Basic HTML stripping
            import re
            try:
                html_body = msg.get_content()
                body = re.sub(r'<[^>]+>', '', html_body)
            except Exception:
                body = ""
    
    return body.strip()


def parse_eml_file(file_path: str) -> List[EmailMessage]:
    """
    Parses EML file and extracts all messages in thread.
    
    Uses Python's built-in email library to:
    1. Parse EML file with proper encoding handling
    2. Extract sender, date, subject, body
    3. Extract thread_id from Message-ID or References headers
    4. Prefer plain text body over HTML
    
    Args:
        file_path: Path to .eml file
        
    Returns:
        List of EmailMessage objects with metadata:
        - sender: email address
        - doc_date: sent timestamp
        - subject: email subject line
        - thread_id: extracted from headers
        - client_keyword: None for manual uploads
        - doc_type: "email"
        - content: email body (plain text preferred)
    """
    # Read and parse EML file
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    
    # Extract sender
    sender = msg.get('From', 'unknown@unknown.com')
    # Clean up sender format (extract email address if in "Name <email>" format)
    if '<' in sender and '>' in sender:
        sender = sender[sender.index('<') + 1:sender.index('>')]
    
    # Extract date
    date_str = msg.get('Date')
    if date_str:
        try:
            doc_date = parsedate_to_datetime(date_str)
        except Exception:
            # Fallback to file modification time
            doc_date = datetime.fromtimestamp(Path(file_path).stat().st_mtime)
    else:
        doc_date = datetime.fromtimestamp(Path(file_path).stat().st_mtime)
    
    # Extract subject
    subject = msg.get('Subject', 'No Subject')
    
    # Extract thread ID
    thread_id = extract_thread_id(msg)
    
    # Extract body
    content = extract_body(msg)
    
    # Create EmailMessage object
    # Note: For manual uploads, client_keyword is None
    # For Gmail API ingestion, this would be set by the calling function
    email_message = EmailMessage(
        sender=sender,
        doc_date=doc_date,
        subject=subject,
        thread_id=thread_id,
        client_keyword=None,  # Set to None for manual uploads
        doc_type="email",
        content=content
    )
    
    # Return as list (single message per EML file)
    # Note: EML files typically contain one message, not full threads
    # Thread reconstruction would happen at the storage layer using thread_id
    return [email_message]

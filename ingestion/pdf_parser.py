"""PDF parsing module for extracting sections with TOC structure."""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import fitz  # PyMuPDF


@dataclass
class PDFSection:
    """Represents a parsed PDF section with metadata."""
    source: str
    section_title: str
    section_number: str
    page_number: int
    doc_date: datetime
    doc_type: str
    content: str


def parse_date_from_filename(filename: str) -> Optional[datetime]:
    """
    Extracts date from filename patterns.
    
    Supported patterns:
    - Refund_Policy_v2_March2024.pdf → 2024-03-01
    - Policy_2024-03-15.pdf → 2024-03-15
    - Doc_Jan2024.pdf → 2024-01-01
    - File_20240315.pdf → 2024-03-15
    
    Args:
        filename: Name of the file (with or without path)
        
    Returns:
        datetime object if date found, None otherwise
    """
    filename = Path(filename).stem  # Remove extension and path
    
    # Pattern 1: YYYY-MM-DD (e.g., 2024-03-15)
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day))
    
    # Pattern 2: YYYYMMDD (e.g., 20240315)
    match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day))
    
    # Pattern 3: Month name + Year (e.g., March2024, Jan2024)
    month_names = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12
    }
    
    for month_name, month_num in month_names.items():
        pattern = rf'{month_name}[_\s-]?(\d{{4}})'
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            year = int(match.group(1))
            return datetime(year, month_num, 1)
    
    # Pattern 4: Year only (e.g., Policy_2024.pdf)
    match = re.search(r'[_\s-](\d{4})[_\s-]', filename)
    if match:
        year = int(match.group(1))
        return datetime(year, 1, 1)
    
    return None


def parse_date_from_content(doc: fitz.Document) -> Optional[datetime]:
    """
    Attempts to extract date from PDF content (first few pages).
    
    Args:
        doc: PyMuPDF document object
        
    Returns:
        datetime object if date found, None otherwise
    """
    # Search first 3 pages for date patterns
    max_pages = min(3, len(doc))
    
    for page_num in range(max_pages):
        page = doc[page_num]
        text = page.get_text()
        
        # Look for common date patterns in content
        # Pattern: "Date: YYYY-MM-DD" or "Effective: March 15, 2024"
        patterns = [
            r'(?:date|effective|published|updated):\s*(\d{4})-(\d{2})-(\d{2})',
            r'(?:date|effective|published|updated):\s*(\w+)\s+(\d{1,2}),?\s+(\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 3 and groups[0].isdigit():
                        # YYYY-MM-DD format
                        return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                    elif len(groups) == 3:
                        # Month Day, Year format
                        month_names = {
                            'january': 1, 'february': 2, 'march': 3, 'april': 4,
                            'may': 5, 'june': 6, 'july': 7, 'august': 8,
                            'september': 9, 'october': 10, 'november': 11, 'december': 12
                        }
                        month = month_names.get(groups[0].lower())
                        if month:
                            return datetime(int(groups[2]), month, int(groups[1]))
                except (ValueError, KeyError):
                    continue
    
    return None


def extract_toc_from_outline(doc: fitz.Document) -> List[dict]:
    """
    Extracts table of contents from PDF outline/bookmarks.
    
    Args:
        doc: PyMuPDF document object
        
    Returns:
        List of dicts with keys: level, title, page, section_number
    """
    toc = doc.get_toc()  # Returns list of [level, title, page]
    
    if not toc:
        return []
    
    # Build hierarchical section numbering
    sections = []
    counters = [0] * 10  # Support up to 10 levels of nesting
    
    for level, title, page in toc:
        # Increment counter at current level
        counters[level - 1] += 1
        # Reset all deeper level counters
        for i in range(level, 10):
            counters[i] = 0
        
        # Build section number (e.g., "2.3.1")
        section_number = '.'.join(str(counters[i]) for i in range(level) if counters[i] > 0)
        
        sections.append({
            'level': level,
            'title': title.strip(),
            'page': page,
            'section_number': section_number
        })
    
    return sections


def extract_text_between_pages(doc: fitz.Document, start_page: int, end_page: int) -> str:
    """
    Extracts text content between two page numbers.
    
    Args:
        doc: PyMuPDF document object
        start_page: Starting page (1-indexed)
        end_page: Ending page (1-indexed, exclusive)
        
    Returns:
        Concatenated text content
    """
    text_parts = []
    
    for page_num in range(start_page - 1, min(end_page - 1, len(doc))):
        page = doc[page_num]
        text_parts.append(page.get_text())
    
    return '\n'.join(text_parts)


def extract_pdf_sections(file_path: str) -> List[PDFSection]:
    """
    Extracts table of contents and named sections from PDF.
    
    Uses PyMuPDF to:
    1. Extract TOC structure from PDF outline/bookmarks
    2. Parse hierarchical section numbering (e.g., "2.3.1")
    3. Extract text content for each section
    4. Parse document date from content or filename
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of PDFSection objects with metadata:
        - source: filename
        - section_title: extracted from TOC
        - section_number: hierarchical numbering (e.g., "2.3.1")
        - page_number: starting page
        - doc_date: parsed from content or filename
        - doc_type: "policy"
        - content: section text
    """
    doc = fitz.open(file_path)
    filename = Path(file_path).name
    
    # Extract date (try content first, then filename, then file modification time)
    doc_date = parse_date_from_content(doc)
    if not doc_date:
        doc_date = parse_date_from_filename(filename)
    if not doc_date:
        # Fallback to file modification time
        doc_date = datetime.fromtimestamp(Path(file_path).stat().st_mtime)
    
    # Extract TOC structure
    toc_sections = extract_toc_from_outline(doc)
    
    if not toc_sections:
        # Fallback: create single section for entire document
        full_text = extract_text_between_pages(doc, 1, len(doc) + 1)
        doc.close()
        
        return [PDFSection(
            source=filename,
            section_title="Full Document",
            section_number="1",
            page_number=1,
            doc_date=doc_date,
            doc_type="policy",
            content=full_text
        )]
    
    # Extract content for each section
    pdf_sections = []
    
    for i, section in enumerate(toc_sections):
        # Determine end page (start of next section or end of document)
        if i + 1 < len(toc_sections):
            end_page = toc_sections[i + 1]['page']
        else:
            end_page = len(doc) + 1
        
        # Extract text content
        content = extract_text_between_pages(doc, section['page'], end_page)
        
        pdf_sections.append(PDFSection(
            source=filename,
            section_title=section['title'],
            section_number=section['section_number'],
            page_number=section['page'],
            doc_date=doc_date,
            doc_type="policy",
            content=content
        ))
    
    doc.close()
    return pdf_sections

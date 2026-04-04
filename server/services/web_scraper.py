"""
Web Scraper Service — scrapes websites and converts to text for ingestion.
"""
import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse
import re


def scrape_website(url: str, max_length: int = 50000) -> dict:
    """
    Scrape a website and convert it to clean text.
    
    Args:
        url: The URL to scrape
        max_length: Maximum text length to extract (default 50000 chars)
    
    Returns:
        dict with:
            - text: Extracted text content
            - title: Page title
            - url: Original URL
            - domain: Domain name
            - word_count: Number of words
            - success: Boolean indicating success
            - error: Error message if failed
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {
                "success": False,
                "error": "Invalid URL format. Please include http:// or https://"
            }
        
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        print(f"🌐 Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else parsed.netloc
        title = title.strip() if title else parsed.netloc
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Method 1: Use html2text for markdown-like conversion
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = False
        h.body_width = 0  # Don't wrap lines
        
        text_content = h.handle(str(soup))
        
        # Clean up the text
        text_content = _clean_text(text_content)
        
        # Truncate if too long
        if len(text_content) > max_length:
            text_content = text_content[:max_length] + "\n\n[Content truncated due to length...]"
        
        # Calculate word count
        word_count = len(text_content.split())
        
        print(f"✅ Successfully scraped: {title}")
        print(f"   Words extracted: {word_count}")
        print(f"   Domain: {parsed.netloc}")
        
        return {
            "success": True,
            "text": text_content,
            "title": title,
            "url": url,
            "domain": parsed.netloc,
            "word_count": word_count,
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. The website took too long to respond."
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection error. Could not reach the website."
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error: {e.response.status_code}. The website returned an error."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to scrape website: {str(e)}"
        }


def _clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Remove lines with only special characters
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Keep line if it has at least some alphanumeric content
        if stripped and re.search(r'[a-zA-Z0-9]', stripped):
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Remove excessive spaces
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def chunk_web_content(text: str, title: str, url: str, chunk_size: int = 1000) -> list:
    """
    Split web content into chunks for embedding.
    
    Args:
        text: The extracted text
        title: Page title
        url: Source URL
        chunk_size: Target size for each chunk (in characters)
    
    Returns:
        List of chunk dictionaries with text and metadata
    """
    chunks = []
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    chunk_num = 1
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # If adding this paragraph would exceed chunk size, save current chunk
        if current_chunk and len(current_chunk) + len(para) > chunk_size:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {
                    "source": title,
                    "source_type": "web",
                    "url": url,
                    "chunk_index": chunk_num,
                    "location": f"Section {chunk_num}"
                }
            })
            current_chunk = para
            chunk_num += 1
        else:
            current_chunk += "\n\n" + para if current_chunk else para
    
    # Add the last chunk
    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "metadata": {
                "source": title,
                "source_type": "web",
                "url": url,
                "chunk_index": chunk_num,
                "location": f"Section {chunk_num}"
            }
        })
    
    print(f"📄 Created {len(chunks)} chunks from web content")
    return chunks

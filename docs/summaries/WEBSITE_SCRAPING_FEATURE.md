# Website Scraping Feature

## Overview

Added the ability to ingest content directly from websites by providing a URL. The system scrapes the webpage, converts it to clean text, and creates vector embeddings for RAG queries.

## Features

### 1. Web Scraping
- **URL Input**: Users can paste any website URL
- **Content Extraction**: Automatically extracts text content from HTML
- **Smart Cleaning**: Removes navigation, scripts, styles, and other non-content elements
- **Markdown Conversion**: Converts HTML to clean, readable text format
- **Length Limiting**: Truncates very long pages (max 50,000 characters)

### 2. Intelligent Chunking
- **Paragraph-Based**: Splits content by paragraphs for better context
- **Optimal Size**: ~1000 characters per chunk
- **Metadata Preservation**: Each chunk includes source URL, title, and section info

### 3. Vector Embedding
- **Same Pipeline**: Uses the same embedding service as file uploads
- **Gemini/Ollama Support**: Works with both embedding providers
- **ChromaDB Storage**: Stores in the same vector database as documents

## How It Works

### User Workflow

1. **Navigate to Documents Page**
2. **Find "Ingest from Website" Section**
3. **Enter URL** (e.g., `https://example.com/article`)
4. **Click "Ingest URL"**
5. **Wait for Scraping** (shows progress)
6. **Content Indexed** (appears in document list)

### Backend Process

```
URL Input
    ↓
Fetch Webpage (with headers to avoid blocking)
    ↓
Parse HTML (BeautifulSoup)
    ↓
Extract Text (html2text)
    ↓
Clean & Normalize
    ↓
Split into Chunks (~1000 chars each)
    ↓
Generate Embeddings (Gemini/Ollama)
    ↓
Store in ChromaDB
    ↓
Save Metadata (title, URL, domain, word count)
```

## Technical Implementation

### Dependencies Added

```txt
beautifulsoup4  # HTML parsing
html2text       # HTML to markdown conversion
```

### New Files

1. **server/services/web_scraper.py**
   - `scrape_website(url)` - Main scraping function
   - `chunk_web_content()` - Splits text into chunks
   - `_clean_text()` - Text cleaning utilities

2. **API Endpoint**: `POST /api/upload-url`
   - Request: `{"url": "https://example.com"}`
   - Response: Success with doc_id, chunks, word count

### Modified Files

1. **server/requirements.txt**
   - Added `beautifulsoup4`
   - Added `html2text`

2. **server/routes/upload.py**
   - Added `URLUploadRequest` model
   - Added `/upload-url` endpoint
   - Updated stats to include "Web URLs"

3. **src/pages/Documents.jsx**
   - Added URL input form
   - Added `handleUrlUpload()` function
   - Added Globe icon for web sources
   - Added purple color scheme for web content

## API Reference

### POST /api/upload-url

Scrape and ingest a website URL.

**Request:**
```json
{
  "url": "https://example.com/article"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "doc_id": "web_a1b2c3d4e5f6",
  "title": "Article Title",
  "url": "https://example.com/article",
  "domain": "example.com",
  "chunks_created": 15,
  "word_count": 3500,
  "embedding_provider": "gemini",
  "message": "Successfully ingested 'Article Title' — 15 chunks indexed from example.com."
}
```

**Error Responses:**

- **400 Bad Request**: Invalid URL, insufficient content, or scraping failed
  ```json
  {
    "detail": "Invalid URL format. Please include http:// or https://"
  }
  ```

- **500 Internal Server Error**: Embedding or storage failed
  ```json
  {
    "detail": "Embedding failed: API key invalid"
  }
  ```

## UI Components

### URL Input Section

Located below the file upload zone in the Documents page:

```
┌─────────────────────────────────────────────────────┐
│ 🌐 Ingest from Website                              │
│    Enter a URL to scrape and index website content  │
│                                                      │
│  🔗 [https://example.com/article    ] [Ingest URL]  │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Globe icon (purple theme)
- URL validation (requires http:// or https://)
- Loading state with spinner
- Progress messages
- Disabled state during scraping

### Document List Display

Web sources appear with:
- **Globe icon** (🌐) in purple
- **Title** as the page title
- **Chunk count** and upload date
- **Status**: "Indexed"
- **Delete button**

## Content Extraction

### What Gets Extracted

✅ **Included:**
- Main article text
- Headings and subheadings
- Paragraphs
- Lists (ordered and unordered)
- Blockquotes
- Tables (converted to text)
- Links (preserved with markdown format)

❌ **Excluded:**
- Navigation menus
- Headers and footers
- Scripts and styles
- Advertisements
- Cookie banners
- Social media widgets

### Text Cleaning

The scraper applies several cleaning steps:

1. **Remove HTML Elements**: Scripts, styles, nav, footer, header
2. **Convert to Markdown**: Using html2text library
3. **Normalize Whitespace**: Remove excessive line breaks
4. **Filter Empty Lines**: Remove lines with only special characters
5. **Preserve Structure**: Keep headings, lists, and formatting

## Error Handling

### Common Errors

1. **Invalid URL**
   - Error: "Invalid URL format. Please include http:// or https://"
   - Solution: Ensure URL starts with http:// or https://

2. **Timeout**
   - Error: "Request timed out. The website took too long to respond."
   - Solution: Try again or use a different URL

3. **Connection Error**
   - Error: "Connection error. Could not reach the website."
   - Solution: Check internet connection and URL validity

4. **HTTP Error**
   - Error: "HTTP error: 404. The website returned an error."
   - Solution: Verify the URL is correct and accessible

5. **Insufficient Content**
   - Error: "Insufficient content extracted from website."
   - Solution: The page may be empty, blocked, or JavaScript-heavy

6. **Blocked by Website**
   - Error: "Failed to scrape website: 403 Forbidden"
   - Solution: Some websites block scrapers; try a different source

## Use Cases

### 1. Documentation Ingestion
```
URL: https://docs.example.com/api-reference
Use: Ingest API documentation for developer queries
```

### 2. Blog Articles
```
URL: https://blog.company.com/best-practices
Use: Add company blog posts to knowledge base
```

### 3. Knowledge Base Articles
```
URL: https://support.company.com/article/123
Use: Import support articles for customer service
```

### 4. Product Pages
```
URL: https://company.com/products/widget
Use: Add product information for sales queries
```

### 5. News Articles
```
URL: https://news.com/industry-update
Use: Keep knowledge base updated with latest news
```

## Limitations

### Current Limitations

1. **JavaScript-Heavy Sites**: May not work well with single-page apps (SPAs)
2. **Authentication**: Cannot scrape pages behind login
3. **Dynamic Content**: Content loaded via JavaScript may not be captured
4. **Rate Limiting**: No built-in rate limiting for multiple URLs
5. **Media Files**: Images, videos, and PDFs embedded in pages are not extracted
6. **Length Limit**: Pages longer than 50,000 characters are truncated

### Workarounds

- **For SPAs**: Use the API endpoint directly or download the page as HTML
- **For Auth Pages**: Download the page manually and upload as a file
- **For Dynamic Content**: Use browser extensions to save the rendered page
- **For Media**: Upload files separately using the file upload feature

## Best Practices

### URL Selection

✅ **Good URLs:**
- Blog posts and articles
- Documentation pages
- Static content pages
- Knowledge base articles
- Product descriptions

❌ **Avoid:**
- Login pages
- Search results
- Dynamic dashboards
- Video streaming pages
- Social media feeds

### Content Quality

- **Verify Content**: Check that the scraped content is accurate
- **Test Queries**: Ask questions to ensure the content is indexed correctly
- **Update Regularly**: Re-scrape pages that change frequently
- **Remove Outdated**: Delete old versions when re-scraping

### Performance

- **Batch Processing**: Scrape multiple URLs during off-peak hours
- **Monitor Errors**: Check logs for failed scrapes
- **Chunk Size**: Default 1000 chars works well for most content
- **Embedding Provider**: Use Gemini for better quality, Ollama for speed

## Testing

### Manual Testing

1. **Start the server**:
   ```bash
   cd server
   pip install beautifulsoup4 html2text
   uvicorn main:app --reload
   ```

2. **Navigate to Documents page**:
   ```
   http://localhost:5173/documents
   ```

3. **Test with a simple URL**:
   ```
   https://example.com
   ```

4. **Verify in document list**:
   - Check for Globe icon
   - Verify title and chunk count
   - Test deletion

5. **Query the content**:
   - Go to Chat page
   - Ask a question about the scraped content
   - Verify the answer includes the web source

### Test URLs

Good test URLs:
- `https://example.com` - Simple test page
- `https://en.wikipedia.org/wiki/Artificial_intelligence` - Rich content
- `https://www.python.org/about/` - Documentation style

### API Testing

```bash
# Test URL upload
curl -X POST http://localhost:8000/api/upload-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Check documents list
curl http://localhost:8000/api/documents

# Check stats
curl http://localhost:8000/api/stats
```

## Future Enhancements

### Potential Improvements

1. **Sitemap Support**: Scrape entire websites from sitemap.xml
2. **Scheduled Re-scraping**: Auto-update content on a schedule
3. **JavaScript Rendering**: Use Selenium/Playwright for SPAs
4. **Authentication**: Support for login-protected pages
5. **Bulk URL Import**: Upload a list of URLs to scrape
6. **Content Diff**: Detect changes and only update modified content
7. **Media Extraction**: Extract and describe images using vision models
8. **Link Following**: Automatically follow and scrape linked pages
9. **Custom Selectors**: Allow users to specify CSS selectors for content
10. **Preview**: Show extracted content before ingesting

## Troubleshooting

### Issue: "Insufficient content extracted"

**Cause**: The page may be JavaScript-heavy or blocked

**Solutions**:
1. Try a different URL
2. Check if the page loads in a browser
3. Use browser dev tools to inspect the HTML
4. Download the page and upload as HTML file

### Issue: "Request timed out"

**Cause**: Website is slow or unresponsive

**Solutions**:
1. Try again later
2. Check your internet connection
3. Verify the URL is correct
4. Try a different page from the same site

### Issue: "HTTP error: 403"

**Cause**: Website is blocking the scraper

**Solutions**:
1. Some websites block automated access
2. Try downloading the page manually
3. Contact the website owner for API access
4. Use the file upload feature instead

### Issue: "No content in chunks"

**Cause**: Content extraction failed

**Solutions**:
1. Check server logs for details
2. Verify the URL returns HTML
3. Test with a simpler URL first
4. Check if the page requires authentication

## Related Documentation

- **FOLDER_WATCH_GUIDE.md**: Automatic file ingestion
- **server/services/parser.py**: File parsing service
- **server/services/embeddings.py**: Embedding generation
- **server/services/vectorstore.py**: Vector storage

## Summary

The website scraping feature extends the Askify RAG system to ingest content from any publicly accessible webpage. It provides a seamless way to add web content to the knowledge base without manual downloading and uploading.

**Key Benefits:**
- ✅ Quick content ingestion from URLs
- ✅ Automatic text extraction and cleaning
- ✅ Same embedding pipeline as files
- ✅ Easy-to-use UI with progress feedback
- ✅ Supports any publicly accessible webpage
- ✅ Integrates seamlessly with existing features

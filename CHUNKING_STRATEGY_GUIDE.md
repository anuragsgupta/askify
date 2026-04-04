# Chunking Strategy Guide

## Overview

This document explains the aggressive preprocessing and chunking strategy implemented to handle large spreadsheets and documents for embedding with Ollama and Gemini.

## Problem

Large spreadsheets with many columns (50+) create chunks that exceed embedding model context limits:
- **Gemini text-embedding-004**: 2048 tokens max
- **Ollama nomic-embed-text**: 8192 tokens max
- **Issue**: Even with 1500 token chunks, wide spreadsheets with 75+ columns created 7260 character chunks that failed

## Solution: Multi-Layer Preprocessing

### 1. Ultra-Conservative Token Limits

**Reduced from 1500 → 1200 tokens per chunk**

```python
MAX_TOKENS = 1200  # ~4800 chars
MAX_VALUE_LENGTH = 200  # Aggressive value truncation
```

This provides a safety margin for:
- Token estimation inaccuracy (1 token ≈ 4 chars is approximate)
- JSON formatting overhead
- Header context in each chunk

### 2. Wide Spreadsheet Detection

Automatically detects spreadsheets with >50 columns and applies aggressive preprocessing:

```python
if num_columns > 50:
    print(f"⚠️  WIDE SPREADSHEET DETECTED ({num_columns} columns)")
    print(f"🔧 Applying aggressive preprocessing")
```

**Preprocessing steps:**
- Truncate all values to 200 chars (reduced from 300)
- Truncate header list in chunk context
- Reduce rows per chunk
- Extra validation for chunk size

### 3. Per-Row Validation

Each row is validated before adding to a chunk:

```python
if row_tokens > MAX_TOKENS * 0.8:  # If single row uses >80% of limit
    # Further truncate this specific row
    if num_columns > 30:
        # Only keep first 30 columns
        truncated_dict = {k: v for i, (k, v) in enumerate(row_dict.items()) if i < 30}
        truncated_dict['_truncated'] = f'... ({num_columns - 30} more columns omitted)'
```

**Benefits:**
- Prevents single oversized rows from breaking chunks
- Maintains most important columns (first 30)
- Clearly marks truncated data

### 4. Multi-Stage Chunk Validation

**Stage 1: During chunk creation**
- Check if adding row exceeds MAX_TOKENS
- Split chunk if limit reached

**Stage 2: Before saving chunk**
- Validate chunk is within limits
- Emergency split if still too large (split in half)

**Stage 3: Final validation**
- Check all chunks with stricter limits (1300 tokens, 5200 chars)
- Emergency split any oversized chunks

### 5. Emergency Split Logic

If a chunk is still too large after preprocessing:

```python
# Split chunk in half
mid = len(current_chunk_rows) // 2
# Save first half
chunk_text = header_text + "\n".join(current_chunk_rows[:mid])
# Save second half
chunk_text = header_text + "\n".join(current_chunk_rows[mid:])
```

## Chunking Limits by File Type

| File Type | Max Tokens | Max Chars | Value Truncation |
|-----------|-----------|-----------|------------------|
| Excel     | 1200      | 4800      | 200 chars        |
| PDF       | 1200      | 4800      | N/A              |
| Text/Email| 1200      | 4800      | N/A              |

## Excel-Specific Features

### Row-Based JSON Format

Each row is converted to JSON for structure preservation:

```json
Row 2:
{
  "Name": "John Doe",
  "Email": "john@example.com",
  "Department": "Engineering",
  ...
}
```

**Benefits:**
- Preserves column-value relationships
- Easy to parse and understand
- Maintains data structure

### Header Context

Each chunk includes header context:

```
Sheet: Sheet1
Columns: Name, Email, Department, ... (75 total columns)

Row 2:
{...}
Row 3:
{...}
```

**For wide spreadsheets (>50 columns):**
```
Sheet: Sheet1
Columns (75 total): Name, Email, Department, ... (75 total columns)
```

### Metadata Tracking

Each chunk includes rich metadata:

```python
{
    "source": "filename.xlsx",
    "source_type": "excel",
    "sheet": "Sheet1",
    "rows": "2-15",
    "row_count": 14,
    "location": "Sheet 'Sheet1', Rows 2-15",
    "format": "json",
    "preprocessed": True  # If aggressive preprocessing was applied
}
```

## Debugging Output

The parser provides detailed logging:

```
📄 PARSING EXCEL: BCA MCA list.xlsx
   Max tokens per chunk: 1200 (ultra-safe for all providers)
   Max value length: 200 chars (aggressive preprocessing)

   📊 Processing sheet: Sheet1
      Columns: 75
      Data rows: 276
      ⚠️  WIDE SPREADSHEET DETECTED (75 columns)
      🔧 Applying aggressive preprocessing:
         - Truncating values to 200 chars
         - Reducing rows per chunk
         - Extra validation for chunk size
      Header tokens: 150
      🔧 Row 2: Truncated 5 value(s) to 200 chars
      ⚠️  Row 2 is very large (980 tokens, 3920 chars)
         This row alone uses 81.7% of chunk limit
         → Reduced to first 30 columns: 650 tokens, 2600 chars
      ✅ Chunk 1: Rows 2-8 (1180 tokens, 4720 chars)
      ✅ Chunk 2: Rows 9-15 (1195 tokens, 4780 chars)
      ...

   🔍 Final validation of all chunks...
   ✅ Excel parsing complete: 45 chunks created
   📊 All chunks are safe for all providers (< 1200 tokens, < 4800 chars)
```

## Best Practices

### For Users

1. **Clean your data before upload:**
   - Remove unnecessary columns
   - Truncate very long text fields
   - Split large spreadsheets into smaller files

2. **Monitor upload logs:**
   - Check for "WIDE SPREADSHEET DETECTED" warnings
   - Review truncation messages
   - Verify chunk counts are reasonable

3. **Test with small samples first:**
   - Upload a few rows to test
   - Verify data quality after chunking
   - Adjust source data if needed

### For Developers

1. **Always use conservative limits:**
   - Token estimation is approximate
   - Leave safety margin for formatting
   - Test with worst-case data

2. **Validate at multiple stages:**
   - During chunk creation
   - Before saving chunks
   - Final validation pass

3. **Provide detailed logging:**
   - Show preprocessing decisions
   - Log truncation events
   - Report final chunk statistics

## Configuration

All limits are defined in `server/services/parser.py`:

```python
# Global limits
MAX_TOKENS = 1200  # Ultra-safe for all providers
MAX_VALUE_LENGTH = 200  # Aggressive value truncation

# Validation thresholds
VALIDATION_TOKEN_LIMIT = 1300  # Final validation
VALIDATION_CHAR_LIMIT = 5200   # Final validation
```

## Testing

To test the chunking strategy:

1. **Upload a wide spreadsheet (50+ columns):**
   ```bash
   # Check backend logs for preprocessing messages
   ./start_backend.sh
   ```

2. **Verify chunk sizes:**
   - All chunks should be < 1200 tokens
   - All chunks should be < 4800 chars
   - No "CHUNK TOO LARGE" errors

3. **Test embedding:**
   - Upload should complete successfully
   - No Ollama context length errors
   - No Gemini token limit errors

## Troubleshooting

### "CHUNK TOO LARGE" Error

**Cause:** Chunk exceeds token limit even after preprocessing

**Solution:**
1. Reduce MAX_TOKENS further (try 1000)
2. Reduce MAX_VALUE_LENGTH (try 150)
3. Reduce column limit for wide rows (try 20 instead of 30)

### "input length exceeds the context length" (Ollama)

**Cause:** Chunk is too large for Ollama's context window

**Solution:**
1. Check if Ollama is using correct model (nomic-embed-text)
2. Verify chunk validation is working
3. Reduce MAX_TOKENS to 1000

### Truncated Data Loss

**Cause:** Aggressive preprocessing removes important data

**Solution:**
1. Clean source data before upload
2. Split wide spreadsheets into multiple files
3. Increase MAX_VALUE_LENGTH if needed (but test carefully)

## Future Improvements

1. **Adaptive chunking:**
   - Adjust limits based on column count
   - Use different strategies for different data types

2. **Smarter column selection:**
   - Identify most important columns
   - Use column names to prioritize

3. **Compression techniques:**
   - Abbreviate common values
   - Use references instead of repetition

4. **User configuration:**
   - Allow users to set chunking preferences
   - Provide chunking preview before upload

## Summary

The multi-layer preprocessing strategy ensures that all documents, including wide spreadsheets with 75+ columns, are safely chunked for embedding with both Ollama and Gemini. The key is aggressive preprocessing, multiple validation stages, and conservative token limits with safety margins.

**Key Numbers:**
- **Max tokens per chunk:** 1200 (ultra-safe)
- **Max value length:** 200 chars (aggressive truncation)
- **Wide spreadsheet threshold:** 50 columns
- **Column limit for wide rows:** 30 columns
- **Final validation limits:** 1300 tokens, 5200 chars

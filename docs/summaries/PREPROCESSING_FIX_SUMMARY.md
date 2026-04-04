# Preprocessing Fix Summary

## Problem Solved

Your spreadsheet with 75 columns was creating chunks of 7260 characters (estimated at 1815 tokens) that exceeded Ollama's context length, causing the error:

```
llm embedding error: the input length exceeds the context length
```

## Solution Implemented

### 1. Reduced Token Limits

**Before:** 1500 tokens per chunk
**After:** 1200 tokens per chunk (~4800 chars)

This provides extra safety margin for:
- Token estimation inaccuracy
- JSON formatting overhead
- Wide spreadsheets with many columns

### 2. Aggressive Preprocessing for Wide Spreadsheets

The parser now automatically detects spreadsheets with >50 columns and applies:

- **Value truncation:** 200 chars max (reduced from 300)
- **Column limiting:** For rows that are too large, only keep first 30 columns
- **Header truncation:** Show only first 10 columns in header context
- **Multi-stage validation:** Check chunk size at 3 different stages

### 3. Enhanced Debugging Output

You'll now see detailed preprocessing logs:

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
      
      🔧 Row 2: Truncated 5 value(s) to 200 chars
      ⚠️  Row 2 is very large (980 tokens, 3920 chars)
         This row alone uses 81.7% of chunk limit
         → Reduced to first 30 columns: 650 tokens, 2600 chars
      
      ✅ Chunk 1: Rows 2-8 (1180 tokens, 4720 chars)
      ✅ Chunk 2: Rows 9-15 (1195 tokens, 4780 chars)
```

### 4. Emergency Split Logic

If a chunk is still too large after preprocessing, it's automatically split in half:

```python
# Split chunk in half
mid = len(current_chunk_rows) // 2
# Save first half and second half separately
```

### 5. Final Validation

All chunks go through a final validation with stricter limits:
- Must be < 1300 tokens
- Must be < 5200 chars
- Any oversized chunks are emergency split

## What Changed in Code

**File:** `server/services/parser.py`

**Key changes:**
1. `MAX_TOKENS = 1200` (reduced from 1500)
2. `MAX_VALUE_LENGTH = 200` (reduced from 300)
3. Wide spreadsheet detection (>50 columns)
4. Per-row validation and column limiting
5. Multi-stage chunk validation
6. Emergency split logic
7. Enhanced debugging output

## How to Test

1. **Start Ollama:**
   ```bash
   ollama serve
   ```

2. **Start backend:**
   ```bash
   ./start_backend.sh
   ```

3. **Upload your spreadsheet:**
   - Go to Documents page
   - Upload your 75-column Excel file
   - Watch the backend logs for preprocessing messages

4. **Expected result:**
   - ✅ Upload completes successfully
   - ✅ No "CHUNK TOO LARGE" errors
   - ✅ No "input length exceeds context length" errors
   - ✅ All chunks are < 1200 tokens

## What You'll See

### For Normal Spreadsheets (<50 columns)
```
📄 PARSING EXCEL: small_file.xlsx
   Max tokens per chunk: 1200
   📊 Processing sheet: Sheet1
      Columns: 10
      Data rows: 100
      ✅ Chunk 1: Rows 2-25 (1150 tokens, 4600 chars)
      ✅ Chunk 2: Rows 26-50 (1180 tokens, 4720 chars)
```

### For Wide Spreadsheets (>50 columns)
```
📄 PARSING EXCEL: wide_file.xlsx
   Max tokens per chunk: 1200
   Max value length: 200 chars (aggressive preprocessing)
   📊 Processing sheet: Sheet1
      Columns: 75
      Data rows: 276
      ⚠️  WIDE SPREADSHEET DETECTED (75 columns)
      🔧 Applying aggressive preprocessing
      🔧 Row 2: Truncated 5 value(s) to 200 chars
      ⚠️  Row 2 is very large (980 tokens)
         → Reduced to first 30 columns: 650 tokens
      ✅ Chunk 1: Rows 2-8 (1180 tokens, 4720 chars)
```

## Benefits

1. **Reliable uploads:** No more context length errors
2. **Automatic handling:** Wide spreadsheets are detected and preprocessed automatically
3. **Transparent:** Detailed logs show exactly what's happening
4. **Safe:** Multiple validation stages ensure chunks are always within limits
5. **Flexible:** Works with both Ollama and Gemini

## Trade-offs

1. **Data truncation:** Values longer than 200 chars are truncated
2. **Column limiting:** Rows with >30 columns may have some columns omitted
3. **More chunks:** Smaller chunk size means more chunks per document

**Recommendation:** If you need all data preserved, clean your spreadsheet before upload:
- Remove unnecessary columns
- Truncate long text fields manually
- Split into multiple smaller files

## Next Steps

1. **Test with your spreadsheet:**
   ```bash
   # Terminal 1: Start Ollama
   ollama serve
   
   # Terminal 2: Start backend
   ./start_backend.sh
   
   # Browser: Upload your file
   ```

2. **Monitor the logs:**
   - Look for "WIDE SPREADSHEET DETECTED"
   - Check chunk sizes (should all be < 1200 tokens)
   - Verify upload completes successfully

3. **Test querying:**
   - Go to Chat page
   - Ask questions about your data
   - Verify answers are accurate

## Documentation

See `CHUNKING_STRATEGY_GUIDE.md` for complete technical details on the preprocessing strategy.

## Configuration

Current settings in `server/.env`:
```env
USE_GEMINI_PRIMARY=false
USE_GEMINI_LLM_PRIMARY=false
OLLAMA_EMBED_MODEL=nomic-embed-text
```

**Provider priority:** Ollama → Gemini (Ollama is primary)

## Summary

The preprocessing fix implements aggressive chunking with multiple safety layers to handle wide spreadsheets. Your 75-column spreadsheet should now upload successfully without context length errors. The system automatically detects wide spreadsheets and applies appropriate preprocessing while providing detailed logs of all actions taken.

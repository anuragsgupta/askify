#!/bin/bash

echo "Testing RAG Query..."
echo ""

# Replace with your actual Gemini API key
API_KEY="${GEMINI_API_KEY:-AIzaSyCnO_7EpEy0Q5wE8t4QQ7LZySGauDkJFzA}"

curl -X POST http://localhost:8000/api/query \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main topics covered in the Ignisia documents?",
    "n_results": 5
  }' | python3 -m json.tool

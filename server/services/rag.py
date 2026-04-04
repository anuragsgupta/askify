"""
RAG Orchestrator — ties together embeddings, vector search,
conflict detection, and LLM answer generation.

Uses Gemini (cloud) as primary LLM, Ollama (local) as fallback.
Configuration via .env file.
"""
import os
from pathlib import Path
import requests
from google import genai
from dotenv import load_dotenv
from server.services.embeddings import embed_query
from server.services.vectorstore import query as vector_query
from server.services.conflict import detect_conflicts

# Load environment variables from server/.env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get configuration from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_LLM_MODEL = os.getenv("GEMINI_LLM_MODEL", "gemini-3-flash-preview")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "qwen3:4b-instruct-2507-q4_K_M")
USE_GEMINI_LLM_PRIMARY = os.getenv("USE_GEMINI_LLM_PRIMARY", "true").lower() == "true"

# Debug: Print configuration on module load
print("\n" + "="*60)
print("🔧 RAG SERVICE CONFIGURATION")
print("="*60)
print(f"📌 .env path: {env_path}")
print(f"📌 .env exists: {env_path.exists()}")
print(f"📌 Gemini API Key: {'✅ SET' if GEMINI_API_KEY else '❌ NOT SET'}")
if GEMINI_API_KEY:
    print(f"📌 Gemini API Key (first 20 chars): {GEMINI_API_KEY[:20]}...")
print(f"📌 Gemini LLM Model: {GEMINI_LLM_MODEL}")
print(f"📌 Ollama LLM Model: {OLLAMA_LLM_MODEL}")
print(f"📌 USE_GEMINI_LLM_PRIMARY: {USE_GEMINI_LLM_PRIMARY}")
print(f"📌 Provider Priority: {'Gemini → Ollama' if USE_GEMINI_LLM_PRIMARY else 'Ollama → Gemini'}")
print("="*60 + "\n")


def generate_answer_ollama(prompt, model=None, temperature=0.0):
    """
    Generate answer using local Ollama model (fallback).
    
    Args:
        prompt: The full prompt with context and question
        model: Ollama model name (optional, uses .env if not provided)
        temperature: LLM temperature (0.0 for deterministic)
        
    Returns:
        Generated text or None if failed
    """
    # Use provided model or fall back to environment variable
    model = model or OLLAMA_LLM_MODEL
    
    print(f"\n🤖 OLLAMA LLM - Starting generation")
    print(f"   Model: {model}")
    print(f"   Prompt length: {len(prompt)} chars (~{len(prompt)//4} tokens)")
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 2048,  # Max tokens to generate
                }
            },
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        
        if "response" in data:
            print(f"✅ OLLAMA LLM - Success (generated {len(data['response'])} chars)")
            return data["response"]
        else:
            print(f"⚠️  OLLAMA LLM - Unexpected response format: {data}")
            return None
            
    except Exception as e:
        print(f"❌ OLLAMA LLM - Failed: {e}")
        return None


def generate_answer_gemini(prompt, api_key=None, model=None):
    """
    Generate answer using Gemini API (primary).
    
    Args:
        prompt: The full prompt with context and question
        api_key: Gemini API key (optional, uses .env if not provided)
        model: Gemini model name (optional, uses .env if not provided)
        
    Returns:
        Generated text or None if failed
    """
    # Use provided values or fall back to environment variables
    api_key = api_key or GEMINI_API_KEY
    model = model or GEMINI_LLM_MODEL
    
    if not api_key:
        print("❌ Gemini API key not found in .env file")
        return None
    
    print(f"\n🌐 GEMINI LLM - Starting generation")
    print(f"   Model: {model}")
    print(f"   Prompt length: {len(prompt)} chars (~{len(prompt)//4} tokens)")
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        
        if response.text:
            print(f"✅ GEMINI LLM - Success (generated {len(response.text)} chars)")
            return response.text
        else:
            print(f"⚠️  GEMINI LLM - Empty response")
            return None
            
    except Exception as e:
        print(f"❌ GEMINI LLM - Failed: {e}")
        return None


def rag_query(question, api_key=None, n_results=10, use_gemini_llm=None):
    """
    Full RAG pipeline:
    1. Embed user question
    2. Retrieve relevant chunks from ChromaDB
    3. Run conflict detection
    4. Generate answer with LLM (Gemini primary, Ollama fallback)
    
    Args:
        question: User's natural language question
        api_key: Gemini API key (optional, uses .env if not provided)
        n_results: Number of chunks to retrieve
        use_gemini_llm: Whether to try Gemini LLM first (optional, uses .env if not provided)
    
    Returns:
        Structured response with answer, sources, and conflicts.
    """
    # Use environment variable if not explicitly set
    if use_gemini_llm is None:
        use_gemini_llm = USE_GEMINI_LLM_PRIMARY
    
    # Use provided API key or fall back to environment variable
    api_key = api_key or GEMINI_API_KEY
    
    print(f"\n{'='*60}")
    print(f"🤖 RAG QUERY PIPELINE")
    print(f"{'='*60}")
    print(f"Question: {question[:100]}{'...' if len(question) > 100 else ''}")
    print(f"Use Gemini LLM Primary: {use_gemini_llm}")
    print(f"Provider Priority: {'Gemini → Ollama' if use_gemini_llm else 'Ollama → Gemini'}")
    print(f"{'='*60}")
    
    # Step 1: Embed the query
    print(f"\n📍 Step 1: Embedding query...")
    query_embedding = embed_query(question, api_key)
    if query_embedding is None:
        print(f"❌ Query embedding failed")
        return {
            "answer": "Could not process your question. Please check your API key.",
            "sources": [],
            "conflict_analysis": {"has_conflicts": False, "conflicts": [], "trusted_sources": []},
        }

    # Step 2: Retrieve relevant chunks
    print(f"\n📍 Step 2: Retrieving relevant chunks from ChromaDB...")
    results = vector_query(query_embedding, n_results=n_results)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    
    print(f"   Retrieved {len(documents)} chunks")

    if not documents:
        print(f"⚠️  No relevant documents found")
        return {
            "answer": "I couldn't find any relevant information in the knowledge base. Please upload some documents first.",
            "sources": [],
            "conflict_analysis": {"has_conflicts": False, "conflicts": [], "trusted_sources": []},
        }

    # Build retrieved chunks list
    retrieved_chunks = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        retrieved_chunks.append({
            "text": doc,
            "metadata": meta,
            "relevance_score": round(1 - dist, 3),  # cosine distance to similarity
        })

    # Step 3: Conflict detection
    print(f"\n📍 Step 3: Running conflict detection...")
    conflict_analysis = detect_conflicts(retrieved_chunks)
    if conflict_analysis["has_conflicts"]:
        print(f"   ⚠️  Conflicts detected: {len(conflict_analysis['conflicts'])} conflict(s)")
    else:
        print(f"   ✅ No conflicts detected")

    # Step 4: Build prompt and generate answer
    print(f"\n📍 Step 4: Building prompt and generating answer...")
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        meta = chunk["metadata"]
        source_label = f"[Source {i}: {meta.get('source', 'Unknown')} — {meta.get('location', '')}]"
        context_parts.append(f"{source_label}\n{chunk['text']}")

    context_text = "\n\n---\n\n".join(context_parts)

    conflict_instruction = ""
    if conflict_analysis["has_conflicts"]:
        conflict_instruction = (
            "\n\nIMPORTANT: Conflicting information was detected across the sources. "
            "You MUST explicitly mention the conflict, state which sources disagree, "
            "and explain that you are trusting the most recently dated source. "
            "Be transparent about the contradiction."
        )

    prompt = f"""You are an AI knowledge assistant for an SME. Answer the user's question based ONLY on the provided document context. Follow these rules strictly:

1. Cite your sources using [Source N] notation for every claim you make.
2. If the information is from an Excel spreadsheet, reference the specific sheet and row.
3. If from a PDF, reference the page number.
4. If from an email/text file, reference the section.
5. If you cannot answer from the provided context, say so clearly.
6. Be precise and professional.{conflict_instruction}

DOCUMENT CONTEXT:
{context_text}

USER QUESTION: {question}

Provide a clear, well-structured answer with citations:"""

    print(f"   Prompt built: {len(prompt)} chars (~{len(prompt)//4} tokens)")
    print(f"   Context chunks: {len(retrieved_chunks)}")
    
    print(f"\n{'='*60}")
    print(f"🤖 LLM GENERATION")
    print(f"{'='*60}")
    print(f"Use Gemini Primary: {use_gemini_llm}")
    print(f"{'='*60}")

    # Try Gemini first (higher quality, faster)
    answer_text = None
    llm_used = None
    
    if use_gemini_llm and api_key:
        print("🌐 Trying Gemini LLM for answer generation...")
        answer_text = generate_answer_gemini(prompt, api_key)
        if answer_text:
            llm_used = f"gemini ({GEMINI_LLM_MODEL})"
            print(f"✅ Gemini generation successful")
        else:
            print("⚠️  Gemini failed, falling back to Ollama...")
    
    # Fallback to Ollama if Gemini failed or not requested
    if not answer_text:
        print("🤖 Using Ollama (local) for answer generation...")
        answer_text = generate_answer_ollama(prompt)
        if answer_text:
            llm_used = f"ollama ({OLLAMA_LLM_MODEL})"
            print(f"✅ Ollama generation successful")
        else:
            print("❌ Both Gemini and Ollama failed")
    
    # Final fallback message
    if not answer_text:
        answer_text = (
            "I was unable to generate a response. "
            "Please check your Gemini API key in server/.env or ensure Ollama is running."
        )
        llm_used = "none (failed)"

    # Build source list for frontend
    sources = []
    seen_sources = set()
    for chunk in retrieved_chunks:
        meta = chunk["metadata"]
        source_key = meta.get("source", "Unknown")
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            sources.append({
                "source": source_key,
                "source_type": meta.get("source_type", "unknown"),
                "location": meta.get("location", ""),
                "relevance_score": chunk["relevance_score"],
                "text_excerpt": chunk["text"][:300],
            })

    print(f"\n{'='*60}")
    print(f"✅ RAG QUERY COMPLETE")
    print(f"{'='*60}")
    print(f"LLM used: {llm_used}")
    print(f"Sources: {len(sources)}")
    print(f"Conflicts: {conflict_analysis['has_conflicts']}")
    print(f"{'='*60}\n")

    return {
        "answer": answer_text,
        "sources": sources,
        "conflict_analysis": conflict_analysis,
        "llm_used": llm_used,  # Show which LLM was used
    }

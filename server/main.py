"""
Askify RAG Backend — FastAPI Application
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables FIRST before importing services
# Find the .env file in the server directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Debug: Print environment loading status
print("\n" + "="*60)
print("🚀 ASKIFY RAG BACKEND STARTING")
print("="*60)
print(f"📌 Working Directory: {os.getcwd()}")
print(f"📌 .env path: {env_path}")
print(f"📌 .env file exists: {env_path.exists()}")
print(f"📌 GEMINI_API_KEY loaded: {'✅ YES' if os.getenv('GEMINI_API_KEY') else '❌ NO'}")
if os.getenv('GEMINI_API_KEY'):
    print(f"📌 GEMINI_API_KEY value: {os.getenv('GEMINI_API_KEY')[:20]}...")
print(f"📌 USE_GEMINI_PRIMARY: {os.getenv('USE_GEMINI_PRIMARY')}")
print(f"📌 USE_GEMINI_LLM_PRIMARY: {os.getenv('USE_GEMINI_LLM_PRIMARY')}")
print(f"📌 GEMINI_LLM_MODEL: {os.getenv('GEMINI_LLM_MODEL')}")
print(f"📌 GEMINI_EMBEDDING_MODEL: {os.getenv('GEMINI_EMBEDDING_MODEL')}")
print("="*60 + "\n")

from server.routes.upload import router as upload_router
from server.routes.query import router as query_router
from server.routes.share import router as share_router
from server.routes.analytics import router as analytics_router
from server.routes.folder_watch import router as folder_watch_router, active_observers
from server.services.folder_watcher import get_watched_folders, start_folder_watcher


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    
    Startup: Initialize watchers for all active folders
    Shutdown: Stop all observers
    """
    # Startup: Initialize watchers for all active folders
    print("\n🔍 Initializing folder watchers...")
    folders = get_watched_folders()
    
    for folder in folders:
        if folder["is_active"]:
            observer, message = start_folder_watcher(folder["folder_path"])
            if observer:
                active_observers[folder["folder_path"]] = observer
                print(f"✅ {message}")
    
    print(f"✅ Started {len(active_observers)} folder watchers\n")
    
    yield
    
    # Shutdown: Stop all observers
    print("\n🛑 Stopping folder watchers...")
    for folder_path, observer in active_observers.items():
        observer.stop()
        observer.join()
        print(f"✅ Stopped watcher for: {folder_path}")


app = FastAPI(title="Askify RAG API", version="1.0.0", lifespan=lifespan)

# CORS — allow Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(upload_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(share_router, prefix="/api")
app.include_router(analytics_router)
app.include_router(folder_watch_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "askify-rag"}

#!/bin/bash

echo "============================================================"
echo "Starting Askify Backend Server"
echo "============================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "server/main.py" ]; then
    echo "❌ Error: server/main.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "❌ FastAPI not installed"
    echo ""
    echo "Installing dependencies..."
    cd server && pip3 install -r requirements.txt
    cd ..
fi

echo "✓ Dependencies installed"
echo ""
echo "Starting FastAPI server..."
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Health Check: http://localhost:8000/api/health"
echo ""
echo "Press CTRL+C to stop the server"
echo "============================================================"
echo ""

# Start the server from project root (not from server/ directory)
python3 -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

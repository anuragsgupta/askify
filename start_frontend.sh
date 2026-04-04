#!/bin/bash

echo "============================================================"
echo "Starting Askify Frontend (React + Vite)"
echo "============================================================"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found"
    echo ""
    echo "Installing dependencies..."
    npm install
fi

echo "✓ Dependencies installed"
echo ""
echo "Starting Vite dev server..."
echo "  - Frontend: http://localhost:5173"
echo ""
echo "Make sure backend is running on http://localhost:8000"
echo "Press CTRL+C to stop the server"
echo "============================================================"
echo ""

# Start the dev server
npm run dev

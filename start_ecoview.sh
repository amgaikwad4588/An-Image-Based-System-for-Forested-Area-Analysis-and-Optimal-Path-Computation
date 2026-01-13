#!/bin/bash

echo ""
echo "========================================"
echo "   EcoView Imaging - Starting Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    echo ""
    exit 1
fi

echo "✓ Python found"
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not available"
    echo "Please install pip3"
    echo ""
    exit 1
fi

echo "✓ pip found"
echo ""

# Install/upgrade dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip > /dev/null 2>&1
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    echo ""
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Start the API server in background
echo "Starting API server..."
python3 PythonScripts/unified_api.py &
API_PID=$!
sleep 3

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $API_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start the web server
echo "Starting web server..."
echo ""
echo "========================================"
echo "   EcoView Imaging is now running!"
echo "========================================"
echo ""
echo "API Server: http://localhost:8000"
echo "Web Interface: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the servers"
echo ""

cd treesense
python3 -m http.server 3000

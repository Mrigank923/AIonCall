#!/bin/bash

# Voice Bot Echo Server Start Script
# ===================================
# Quick start script for the Exotel echo server

set -e

echo "🚀 Starting Voice Bot Echo Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if port 5000 is available
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 5000 is already in use. Stopping existing processes..."
    lsof -ti:5000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start the server
echo "🎯 Starting echo server on port 5000..."
echo "📝 Logs will be displayed here and saved to logs/voice_bot_echo.log"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

python3.8 simple_server.py 

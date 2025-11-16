#!/bin/bash
# spyTrade Application Startup Script
# This script sets up and launches the spyTrade dashboard

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    spyTrade Startup Script                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python $(python3 --version | awk '{print $2}') detected"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run this script from the spyTrade directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install/upgrade dependencies
echo ""
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys (optional, see SETUP.md)"
fi

# Start the application
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║            Starting spyTrade Dashboard...                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Dashboard will open in your browser at: http://localhost:5000"
echo "📊 Features:"
echo "   ✓ Real-time price charts"
echo "   ✓ Technical indicators (RSI, MACD, SMA)"
echo "   ✓ Trade signals with confidence scores"
echo "   ✓ News sentiment analysis"
echo "   ✓ Risk/reward calculations"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Run the dashboard
python dashboard.py

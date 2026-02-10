#!/bin/bash
# X-Wise News Crawler - Startup Script

echo "============================================================"
echo "X-Wise News Crawler - Starting..."
echo "============================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check database connection
echo ""
echo "🔍 Checking database connection..."
python test_setup.py

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Please check .env configuration."
    exit 1
fi

echo ""
echo "✅ Database connection OK"
echo ""
echo "============================================================"
echo "Starting crawler in SCHEDULER mode..."
echo "============================================================"
echo ""
echo "📋 Crawler will run automatically based on schedule:"
echo "   - VnExpress: Every 2 hours"
echo "   - Blockchain sources: Every 3 hours"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start crawler in scheduler mode
python main.py --mode scheduler

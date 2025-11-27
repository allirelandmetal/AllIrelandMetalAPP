#!/bin/bash
# Cleanup script to remove virtual environment and build artifacts

echo "🧹 Cleaning up Irish Metal App project..."
echo "======================================"

# Remove virtual environment directory
if [ -d "metal" ]; then
    echo "🗑️  Removing virtual environment (metal/)..."
    rm -rf metal/
    echo "✅ Virtual environment removed"
else
    echo "ℹ️  No virtual environment found (metal/)"
fi

# Remove build artifacts
echo "🗑️  Removing build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf __pycache__/
rm -f *.spec
rm -f *.pyc

# Remove any .DS_Store files on macOS
find . -name ".DS_Store" -delete 2>/dev/null

# Remove cache files
rm -f cache.sqlite

echo "✅ Cleanup complete!"
echo ""
echo "📋 To set up the project again, run:"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
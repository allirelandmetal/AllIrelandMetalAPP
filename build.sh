#!/bin/bash
# Simple build script for creating macOS executable

echo "🎸 Building Irish Metal App for macOS 🤘"
echo "======================================"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Using virtual environment: $VIRTUAL_ENV"
else
    echo "⚠️  Not in a virtual environment. Consider creating one with:"
    echo "   python -m venv venv && source venv/bin/activate"
    echo "   Continuing anyway..."
fi

# Install PyInstaller if not installed
echo "📦 Installing PyInstaller..."
pip install pyinstaller

# Install requirements
echo "📋 Installing requirements..."
pip install -r requirements.txt

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec

# Build the executable
echo "🔨 Building executable..."
pyinstaller --onefile \
    --console \
    --name "IrishMetalApp" \
    --add-data "requirements.txt:." \
    --hidden-import "urllib3" \
    --hidden-import "pyquery" \
    --hidden-import "lxml" \
    --hidden-import "cssselect" \
    --hidden-import "requests" \
    irish_metal_app.py

# Check if build was successful
if [ -f "dist/IrishMetalApp" ]; then
    echo "✅ Build successful!"
    echo "📁 Executable created: dist/IrishMetalApp"
    echo ""
    echo "🎯 You can now run the app with:"
    echo "   ./dist/IrishMetalApp"
    echo ""
    echo "📦 To distribute, copy the 'dist/IrishMetalApp' file to other Macs"
    
    # Make executable
    chmod +x dist/IrishMetalApp
    
    # Test the executable
    echo "🧪 Testing executable..."
    echo "(This will run the app - press Ctrl+C to exit after testing)"
    echo ""
    ./dist/IrishMetalApp
else
    echo "❌ Build failed!"
    echo "Check the output above for errors."
fi
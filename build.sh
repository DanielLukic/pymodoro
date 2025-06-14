#!/bin/bash

echo "🚀 Building Pymodoro executable..."

# Install PyInstaller if not present
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
rm -rf dist/ build/ *.spec

# Build the executable
echo "🔨 Creating executable..."
pyinstaller \
    --onefile \
    --windowed \
    --name=pymodoro \
    --add-data="pymodoro:pymodoro" \
    --hidden-import=pynput.keyboard._xorg \
    --hidden-import=pynput.mouse._xorg \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtWidgets \
    --hidden-import=PyQt6.QtGui \
    run.py

if [ -f "dist/pymodoro" ]; then
    chmod +x dist/pymodoro
    SIZE=$(du -h dist/pymodoro | cut -f1)
    echo ""
    echo "🎉 BUILD SUCCESSFUL!"
    echo "📦 Executable: dist/pymodoro"
    echo "📏 Size: $SIZE"
    echo ""
    echo "To install system-wide:"
    echo "  sudo cp dist/pymodoro /usr/local/bin/"
    echo ""
    echo "To add to applications menu:"
    echo "  cp pymodoro.desktop ~/.local/share/applications/"
    echo ""
    echo "Run with: ./dist/pymodoro"
else
    echo "❌ Build failed!"
    exit 1
fi 
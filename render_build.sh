#!/bin/bash
# Render build script for AnomiDate Web

echo "🚀 Starting AnomiDate Web build..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies for CSS build
echo "📦 Installing Node.js dependencies..."
npm install

# Build CSS for production
echo "🎨 Building CSS for production..."
python build_css.py

echo "✅ Build complete!"

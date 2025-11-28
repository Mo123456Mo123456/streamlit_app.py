#!/bin/bash

# AI Economic Analysis Dashboard - Setup Script
# Educational Tool Only - Not Financial Advice

echo "🤖 AI Economic Analysis Dashboard Setup"
echo "========================================"
echo ""

# Check Python installation
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version)
    echo "✅ Found: $PYTHON_VERSION"
else
    echo "❌ Error: Python is not installed"
    echo "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

echo ""

# Check pip installation
echo "Checking pip installation..."
if $PYTHON_CMD -m pip --version &> /dev/null; then
    PIP_VERSION=$($PYTHON_CMD -m pip --version)
    echo "✅ Found: $PIP_VERSION"
else
    echo "❌ Error: pip is not installed"
    echo "Please install pip: https://pip.pypa.io/en/stable/installation/"
    exit 1
fi

echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
echo ""

if $PYTHON_CMD -m pip install -r requirements.txt; then
    echo ""
    echo "✅ Dependencies installed successfully!"
else
    echo ""
    echo "❌ Error installing dependencies"
    echo "Please try running: $PYTHON_CMD -m pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "To start the application, run:"
echo ""
echo "  streamlit run streamlit_app.py"
echo ""
echo "Or:"
echo ""
echo "  $PYTHON_CMD -m streamlit run streamlit_app.py"
echo ""
echo "⚠️  IMPORTANT REMINDER:"
echo "This is an EDUCATIONAL tool only."
echo "NOT for actual investment decisions."
echo "Read DISCLAIMER.md before using."
echo ""
echo "Happy learning! 🚀"

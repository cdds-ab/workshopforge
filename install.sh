#!/bin/bash
# WorkshopForge Installation Script
# Usage: curl -sSL https://raw.githubusercontent.com/cdds-ab/workshopforge/main/install.sh | bash

set -e

echo "🔨 Installing WorkshopForge..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Check Python version
PYTHON_VERSION=$(uv python list | grep -E "3\.(10|11|12)" | head -1 | awk '{print $2}' || echo "")

if [ -z "$PYTHON_VERSION" ]; then
    echo "📦 Installing Python 3.11..."
    uv python install 3.11
    PYTHON_VERSION="3.11"
fi

echo "✓ Using Python $PYTHON_VERSION"

# Install workshopforge as a tool
echo "📦 Installing workshopforge..."
uv tool install --python $PYTHON_VERSION git+https://github.com/cdds-ab/workshopforge.git

echo ""
echo "✅ WorkshopForge installed successfully!"
echo ""
echo "Usage:"
echo "  workshopforge init my-workshop     # Create new workshop"
echo "  workshopforge --help               # Show all commands"
echo ""
echo "Note: Make sure ~/.local/bin is in your PATH"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""

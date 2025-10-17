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

# Check if Python 3.10+ is available
PYTHON_CMD=""
for py_version in python3.12 python3.11 python3.10 python3; do
    if command -v $py_version &> /dev/null; then
        PY_VERSION=$($py_version --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        MAJOR=$(echo $PY_VERSION | cut -d. -f1)
        MINOR=$(echo $PY_VERSION | cut -d. -f2)
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON_CMD=$py_version
            echo "✓ Found Python $PY_VERSION"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "📦 Installing Python 3.11..."
    uv python install 3.11
    PYTHON_CMD="python3.11"
fi

# Install workshopforge as a tool
echo "📦 Installing workshopforge..."
uv tool install git+https://github.com/cdds-ab/workshopforge.git

echo ""
echo "✅ WorkshopForge installed successfully!"
echo ""
echo "Usage:"
echo "  workshopforge init my-workshop     # Create new workshop"
echo "  workshopforge --help               # Show all commands"
echo ""
echo "Note: Make sure ~/.local/bin is in your PATH"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""

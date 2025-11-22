#!/bin/bash
# Setup script for SMTP Client
# Installs npm dependencies

set +e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "SMTP Client - Setup"
echo "==================="
echo ""

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    if ! npm install --silent; then
        echo "⚠ npm install failed, trying to fix permissions..."
        sudo chown -R $(whoami) ~/.npm 2>/dev/null || true
        npm install --silent || {
            echo "✗ Failed to install dependencies. Please run: sudo chown -R $(whoami) ~/.npm"
            exit 1
        }
    fi
    echo "✓ Dependencies installed"
else
    echo "Dependencies already installed"
fi

echo ""
echo "Setup complete!"
echo ""


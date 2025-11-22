#!/bin/bash
# Setup script for MailGuard Server
# Creates venv, installs dependencies, creates .env, and sets up Tika

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "MailGuard Server - Setup"
echo "========================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! python3 --version; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Create venv only if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "Installing/updating Python dependencies..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
else
    echo "Virtual environment found, activating..."
    source .venv/bin/activate
    echo "Checking dependencies..."
    pip install -q -r requirements.txt
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    python3 -c "import secrets; print(secrets.token_hex(32))" > /tmp/secret_key.txt
    SECRET_KEY=$(cat /tmp/secret_key.txt)
    rm /tmp/secret_key.txt
    
    cat > .env << EOF
# SMTP Proxy Configuration
PROXY_HOST=0.0.0.0
PROXY_PORT=2525
UPSTREAM_SMTP_HOST=smtp.example.com
UPSTREAM_SMTP_PORT=25

# Apache Tika Configuration
TIKA_SERVER_URL=http://localhost:9998

# Flask UI Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=False
SECRET_KEY=$SECRET_KEY

# Database Configuration
DATABASE_URL=sqlite:///mailguard.db

# Policy Configuration
DEFAULT_POLICY=tag
MAX_ATTACHMENT_SIZE_MB=50
MAX_ARCHIVE_DEPTH=5

# Detection Thresholds
MIN_CONFIDENCE=0.7
ENABLE_SPACY=true

# Quarantine Configuration
QUARANTINE_DIR=./quarantine
EOF
    echo ".env file created"
    mkdir -p quarantine
fi

# Install spaCy model (optional, skip if SKIP_SPACY is set)
if [ -z "$SKIP_SPACY" ]; then
    echo ""
    echo "Note: spaCy is optional. The system works without it (regex detection only)."
    read -p "Install spaCy English model? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        source .venv/bin/activate
        echo "Downloading spaCy English model..."
        if python -m spacy download en_core_web_sm 2>&1; then
            echo "✓ spaCy model installed successfully"
        else
            echo ""
            echo "⚠ Warning: Could not download spaCy model. The system will work without it."
            echo "  The regex-based detection will still work fine."
            echo "  To try installing later: python -m spacy download en_core_web_sm"
            echo "  Or set ENABLE_SPACY=false in .env to disable spaCy features"
        fi
    fi
fi

# Setup Tika
echo ""
echo "Setting up Apache Tika server..."
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

set +e
if command_exists docker; then
    if docker info >/dev/null 2>&1; then
        echo "Starting Tika server..."
        docker-compose up -d >/dev/null 2>&1 || echo "(Tika may already be running)"
        echo "✓ Tika server ready"
    else
        echo "⚠ Docker is not running. Tika features may not work."
    fi
else
    echo "⚠ Docker not found. Tika features may not work."
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source .venv/bin/activate"
echo "2. Start MailGuard: python main.py"
echo "3. Access the dashboard: http://localhost:5001"
echo ""


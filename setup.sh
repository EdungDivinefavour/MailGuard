#!/bin/bash
# Setup script for Email Interceptor

# Don't exit on error for optional steps
set +e

echo "Email Interceptor - Setup Script"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! python3 --version; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
if ! pip install -r requirements.txt; then
    echo "Error: Failed to install dependencies. Please check the error above."
    exit 1
fi

# Install spaCy model (optional)
echo ""
echo "Note: spaCy is optional. The system works without it (regex detection only)."
read -p "Install spaCy English model? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
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

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
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
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Database Configuration
DATABASE_URL=sqlite:///email_interceptor.db

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
    echo ".env file created. Please edit it with your settings."
else
    echo ".env file already exists, skipping..."
fi

# Create quarantine directory
echo "Creating quarantine directory..."
mkdir -p quarantine

# Start Tika server
echo ""
echo "Starting Apache Tika server with Docker..."
if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
    docker-compose up -d || {
        echo "⚠ Warning: Could not start Tika server. You can start it manually with: docker-compose up -d"
    }
else
    echo "⚠ Warning: Docker not found. Please install Docker and run: docker-compose up -d"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "2. Activate virtual environment: source .venv/bin/activate"
echo "3. Start the interceptor: python main.py"
echo "4. Access the dashboard: http://localhost:5001"
echo ""


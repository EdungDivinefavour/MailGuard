#!/bin/bash
# Start script for MailGuard - Sets up and starts all services

# Don't exit on error for npm installs (they might have permission issues)
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   MailGuard - Startup Script          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Re-enable exit on error for critical parts
set -e

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
MISSING_DEPS=()

if ! command_exists python3; then
    MISSING_DEPS+=("Python 3")
fi

if ! command_exists node; then
    MISSING_DEPS+=("Node.js")
fi

if ! command_exists npm; then
    MISSING_DEPS+=("npm")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "${RED}✗ Missing dependencies:${NC}"
    for dep in "${MISSING_DEPS[@]}"; do
        echo -e "  - $dep"
    done
    echo ""
    echo "Please install the missing dependencies and try again."
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites found${NC}"
echo ""

# Setup MailGuard Server (includes Tika setup)
echo -e "${YELLOW}Setting up MailGuard Server...${NC}"
cd "$SCRIPT_DIR/mailguard-server"
# Run setup but skip interactive spaCy prompt
SKIP_SPACY=1 ./setup.sh
echo -e "${GREEN}✓ MailGuard Server setup complete${NC}"
echo ""

# Setup MailGuard Client
echo -e "${YELLOW}Setting up MailGuard Client...${NC}"
cd "$SCRIPT_DIR/mailguard-client"
./setup.sh
echo -e "${GREEN}✓ MailGuard Client setup complete${NC}"
echo ""

# Setup SMTP Client
echo -e "${YELLOW}Setting up SMTP Client...${NC}"
cd "$SCRIPT_DIR/smtp-client"
./setup.sh
echo -e "${GREEN}✓ SMTP Client setup complete${NC}"
echo ""

# Create a function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $SERVER_PID 2>/dev/null || true
    kill $DASHBOARD_PID 2>/dev/null || true
    kill $CLIENT_PID 2>/dev/null || true
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start MailGuard Server
echo -e "${BLUE}Starting MailGuard Server...${NC}"
cd "$SCRIPT_DIR/mailguard-server"

# Activate the virtual environment (should already exist from setup)
source .venv/bin/activate
python main.py > /tmp/mailguard-server.log 2>&1 &
SERVER_PID=$!
echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"
echo "  - SMTP Proxy: localhost:2525"
echo "  - Flask API: http://localhost:5001"
echo ""

# Wait a bit for server to start
sleep 3

# Start MailGuard Dashboard
echo -e "${BLUE}Starting MailGuard Dashboard...${NC}"
cd "$SCRIPT_DIR/mailguard-client"
npm run dev > /tmp/mailguard-dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo -e "${GREEN}✓ Dashboard started (PID: $DASHBOARD_PID)${NC}"
echo "  - URL: http://localhost:3000"
echo ""

# Start SMTP Client
echo -e "${BLUE}Starting SMTP Client...${NC}"
cd "$SCRIPT_DIR/smtp-client"
npm run dev > /tmp/smtp-client.log 2>&1 &
CLIENT_PID=$!
echo -e "${GREEN}✓ Email Client started (PID: $CLIENT_PID)${NC}"
echo "  - URL: http://localhost:3001"
echo ""

# Summary
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   All Services Started!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Services:${NC}"
echo "  📧 SMTP Proxy:     localhost:2525"
echo "  🔌 Flask API:      http://localhost:5001"
echo "  📊 Dashboard:      http://localhost:3000"
echo "  ✉️  Email Client:   http://localhost:3001"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "  Server:    tail -f /tmp/mailguard-server.log"
echo "  Dashboard: tail -f /tmp/mailguard-dashboard.log"
echo "  Client:    tail -f /tmp/smtp-client.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""
echo -e "${BLUE}Server logs:${NC}"
echo ""

# Show server logs in current tab
tail -f /tmp/mailguard-server.log
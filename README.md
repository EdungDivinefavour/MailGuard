# MailGuard - Data Leakage Prevention (DLP) Proxy

SMTP proxy that sits between your mail client and the mail server. It intercepts emails, checks for sensitive data, and can block, sanitize, quarantine, or tag them.

## Project Structure

This project consists of three main components:

1. **MailGuard Server** - SMTP proxy and Flask API (Python)
2. **MailGuard Dashboard** - Admin dashboard to view intercepted emails (React)
3. **SMTP Email Client** - Email client for users to send/receive emails (React)

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure.

## Quick Start

### Option 1: One-Command Startup (Recommended)

Run everything with a single command:

```bash
./start.sh
```

This script will:
- Check prerequisites (Python, Node.js, npm)
- Set up the MailGuard server (virtual environment, dependencies)
- Install dependencies for both React apps
- Start Tika server (if Docker is available)
- Start all three services:
  - MailGuard Server (SMTP proxy + Flask API)
  - MailGuard Dashboard (React)
  - SMTP Email Client (React)

**On Windows:** Use `.\start.ps1` instead

### Option 2: Manual Setup

If you prefer to set up and run services manually:

#### 1. Setup Server

```bash
cd mailguard-server
./setup.sh
```

Sets up the virtual environment, installs dependencies, starts Tika, and creates the config file. You'll be prompted to optionally install spaCy.

#### 2. Start MailGuard Server

```bash
cd mailguard-server
source .venv/bin/activate
python main.py
```

This starts:
- SMTP proxy on port 2525
- Flask API on port 5001

#### 3. Setup and Start MailGuard Dashboard

```bash
cd mailguard-client
./setup.sh
npm run dev
```

Access the dashboard at: `http://localhost:3000`

#### 4. Setup and Start Email Client

```bash
cd smtp-client
./setup.sh
npm run dev
```

Access the email client at: `http://localhost:3001`

## Usage

### Testing with Email Client

1. Open the email client at `http://localhost:3001`
2. Enter your email address when prompted
3. Compose and send emails to other users
4. View sent/received emails in the inbox and sent folders

### Testing with Test Script

```bash
cd mailguard-server
python test_email.py
```

Pick a test email from the menu, then check the dashboard at `http://localhost:3000`

## Configuration

The setup script creates a `.env` file. Edit it to change settings:

```env
# SMTP Proxy
PROXY_HOST=0.0.0.0
PROXY_PORT=2525
UPSTREAM_SMTP_HOST=smtp.example.com
UPSTREAM_SMTP_PORT=25

# Flask UI
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# Policy
DEFAULT_POLICY=tag  # block, sanitize, quarantine, or tag
```

## Features

- SMTP proxy that intercepts emails before they're sent
- Extracts text from attachments (PDF, DOCX, ZIP, etc.) using Apache Tika
- Detects credit cards, SINs, SSNs, and email addresses using regex
- Can block, sanitize, quarantine, or tag emails with sensitive data
- Web dashboard to view intercepted emails and stats
- Email client for users to send/receive emails with real-time updates
- Download email attachments directly from the email client
- WebSocket support for instant inbox updates

## API Endpoints

- `GET /api/emails` - Get email logs (with pagination/filters)
- `GET /api/emails/<id>` - Get specific email details
- `GET /api/stats` - Get statistics
- `POST /api/send-email` - Send email via SMTP proxy
- `GET /api/attachments/<id>/download` - Download email attachment

## Detection Patterns

- Credit cards: `XXXX-XXXX-XXXX-XXXX` format
- SIN (Canadian): `XXX-XXX-XXX` format
- SSN (US): `XXX-XX-XXXX` format
- Email addresses: standard email format

## Policy Actions

- `block`: Don't send the email
- `sanitize`: Replace sensitive data with `[REDACTED]`
- `quarantine`: Save to quarantine folder
- `tag`: Add warning headers (default)

## Requirements

- Python 3.8+
- Node.js 16+ (for React frontends)
- Docker (for Apache Tika)

For more details, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

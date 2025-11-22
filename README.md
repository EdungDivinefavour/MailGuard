# MailGuard - Data Leakage Prevention (DLP) Proxy

SMTP proxy that sits between your mail client and the mail server. It intercepts emails, checks for sensitive data, and can block, sanitize, quarantine, or tag them.

## Quick Start

### 1. Setup

```bash
./setup.sh
```

Sets up the virtual environment, installs dependencies, starts Tika, and creates the config file.

### 2. Start MailGuard

```bash
python main.py
```

Runs the SMTP proxy on port 2525 and the web dashboard on port 5001.

### 3. Test It

Open a new terminal and run:
```bash
python test_email.py
```

Pick a test email from the menu, then check the dashboard at `http://localhost:5001`

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

# Optional: spaCy for enhanced detection
ENABLE_SPACY=false
```

## Features

- SMTP proxy that intercepts emails before they're sent
- Extracts text from attachments (PDF, DOCX, ZIP, etc.) using Apache Tika
- Detects credit cards, SINs, SSNs, and email addresses using regex
- Can block, sanitize, quarantine, or tag emails with sensitive data
- Web dashboard to view intercepted emails and stats

## Usage

Point your mail client to use the proxy:
- SMTP Server: `localhost`
- SMTP Port: `2525`

The proxy forwards emails to your upstream SMTP server after checking them.

For more details, see [QUICKSTART.md](QUICKSTART.md).

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
- Docker (for Apache Tika)

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Get started quickly
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Code organization

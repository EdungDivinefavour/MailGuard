# Email Interceptor - Data Leakage Prevention (DLP) Proxy

An inline SMTP proxy that intercepts outbound emails, inspects content, and enforces data leakage prevention policies (block, sanitize, quarantine, or tag).

## Quick Start

### 1. Setup

```bash
./setup.sh
```

This handles everything: virtual environment, dependencies, Tika server, and configuration.

### 2. Start the Interceptor

```bash
python main.py
```

This starts:
- **SMTP Proxy** on port `2525` (intercepts emails)
- **Web Dashboard** on port `5001` (view logs)

### 3. Test It

In a new terminal:
```bash
python test_email.py
```

Choose a test email from the menu. Then check the dashboard at `http://localhost:5001`

## Configuration

Create a `.env` file (or edit the one created by setup.sh):

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

- **SMTP Proxy**: Intercepts emails between mail relay and outbound server
- **Content Extraction**: Extracts text from attachments (PDF, DOCX, ZIP, etc.) using Apache Tika
- **Detection**: Regex patterns for credit cards, SINs, SSNs, email addresses
- **Policy Actions**: Block, sanitize, quarantine, or tag emails with sensitive data
- **Web Dashboard**: Monitor intercepted emails, view detection results, and statistics

## Project Structure

```
email_interceptor/
├── email_interceptor/          # Main package
│   ├── config.py              # Configuration
│   ├── engines/               # Processing engines
│   │   ├── detection_engine.py
│   │   ├── content_extractor.py
│   │   └── policy_engine.py
│   ├── models/                # Database models
│   │   ├── email.py
│   │   ├── recipient.py
│   │   └── attachment.py
│   └── proxy/                 # SMTP proxy
│       └── smtp_proxy.py
├── app.py                     # Flask web app
├── main.py                    # Entry point
├── test_email.py              # Test script
├── static/                    # CSS/JS
├── templates/                 # HTML templates
└── test_emails/               # Test email samples
```

## Usage

### Send Test Emails

```bash
python test_email.py
```

Interactive menu to choose from various test email types.

### Access Dashboard

Open `http://localhost:5001` in your browser to:
- View intercepted emails
- See detection results
- Filter by flagged/status
- View statistics

### Configure Mail Client

Point your mail client to use the proxy:
- **SMTP Server**: `localhost`
- **SMTP Port**: `2525`

The proxy will forward to your configured upstream SMTP server.

## Detection Patterns

- **Credit Cards**: Format `XXXX-XXXX-XXXX-XXXX`
- **SIN (Social Insurance Number)**: Canadian format `XXX-XXX-XXX`
- **SSN (Social Security Number)**: US format `XXX-XX-XXXX`
- **Email Addresses**: Standard email format

## Policy Actions

- **block**: Prevent email from being sent
- **sanitize**: Remove sensitive data, replace with `[REDACTED]`
- **quarantine**: Save email to quarantine directory
- **tag**: Add warning headers to email (default)

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Requirements

- Python 3.8+
- Docker (for Apache Tika - handled by setup.sh)

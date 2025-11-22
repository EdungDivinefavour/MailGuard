# Email Interceptor - Data Leakage Prevention (DLP) Proxy

An inline SMTP proxy that intercepts outbound emails and attachments, inspects their content, and enforces data leakage prevention policies (block, sanitize, quarantine, or tag).

## Quick Start

**New to this project?** See [QUICKSTART.md](QUICKSTART.md) for step-by-step instructions.

**Want to test it?** See [TESTING.md](TESTING.md) for comprehensive testing guide.

## Features

- **SMTP Proxy**: Intercepts emails between local mail relay and outbound mail server
- **Content Extraction**: Uses Apache Tika to extract text from various file formats (PDF, DOCX, ZIP, etc.)
- **Detection Engine**: 
  - Regex patterns for credit cards, SINs, SSNs, emails, phone numbers, IP addresses
  - Optional spaCy-based Named Entity Recognition (NER) for sensitive information
- **Policy Enforcement**: 
  - **Block**: Prevent email from being sent
  - **Sanitize**: Remove sensitive data and replace with [REDACTED]
  - **Quarantine**: Save email to quarantine directory
  - **Tag**: Add warning headers to email
- **Web Dashboard**: Flask-based UI for monitoring logs and flagged messages
- **Performance Metrics**: Track processing latency and throughput

## Architecture

```
Local Mail Relay → SMTP Proxy (Port 2525) → Upstream SMTP Server
                         ↓
              Content Extraction (Tika)
                         ↓
              Detection Engine (Regex + spaCy)
                         ↓
              Policy Engine (Block/Sanitize/Quarantine/Tag)
                         ↓
              Database Logging + Web UI
```

## Prerequisites

- Python 3.8+
- Docker and Docker Compose (for Apache Tika)
- (Optional) spaCy English model: `python -m spacy download en_core_web_sm`

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd email_interceptor
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install spaCy model (optional but recommended):**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Start Apache Tika server:**
   ```bash
   docker-compose up -d
   ```

6. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Configuration

Edit `.env` file or set environment variables:

```env
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
SECRET_KEY=your-secret-key-here

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
```

## Usage

### Start the Email Interceptor

```bash
python main.py
```

This will start:
- SMTP proxy on port 2525 (configurable)
- Flask web UI on port 5001 (configurable)

### Configure Your Mail Server

Point your local mail relay to use the proxy:

```
Original: Local Relay → smtp.example.com:25
New:      Local Relay → localhost:2525 → smtp.example.com:25
```

### Access the Web Dashboard

Open your browser to: `http://localhost:5001`

The dashboard shows:
- Statistics (total emails, flagged, blocked, quarantined)
- Email logs with filtering options
- Detection results and applied policies
- Performance metrics

## Detection Patterns

The system detects:

- **Credit Cards**: Format XXXX-XXXX-XXXX-XXXX
- **SIN (Social Insurance Number)**: Canadian format (XXX-XXX-XXX)
- **SSN (Social Security Number)**: US format (XXX-XX-XXXX)
- **Email Addresses**: Standard email format
- **Named Entities** (optional spaCy): Persons, Organizations

## Policy Rules

Default policy actions by detection type:

- `credit_card`, `sin`, `ssn`: **Block**
- `email`, `ner_person`, `ner_org`: **Tag**

You can customize policies in `policy_engine.py`.

## Metrics

The system tracks:

- **Performance**: Processing latency per email
- **Detection Results**: What patterns were detected in each email
- **Policy Actions**: What action was taken (block, tag, sanitize, quarantine)

## Project Structure

```
email_interceptor/
├── main.py                 # Main entry point
├── config.py              # Configuration management
├── smtp_proxy.py          # SMTP proxy server
├── detection_engine.py    # Pattern detection logic
├── content_extractor.py   # Tika integration
├── policy_engine.py       # Policy enforcement
├── models.py              # Database models
├── app.py                 # Flask web application
├── templates/
│   └── index.html        # Web dashboard
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Tika server setup
├── .env.example          # Environment template
└── README.md             # This file
```

## Testing

### Test Email with Sensitive Data

You can test the system by sending an email through the proxy:

```bash
python test_email.py --type sensitive
```

Or use the demo script to test detection directly:

```bash
python demo.py
```

## Limitations and Considerations

- **Encrypted Payloads**: Cannot inspect encrypted/S/MIME emails
- **File Size Limits**: Large attachments may timeout (configurable)
- **Archive Depth**: Nested archives limited by MAX_ARCHIVE_DEPTH
- **Performance**: Processing adds latency (typically < 1 second per email)
- **False Positives**: Some patterns (like phone numbers) may have high false positive rates
- **Bypass Scenarios**: Trusted flows may need whitelisting

## Troubleshooting

### Tika Server Not Available

```bash
# Check if Tika is running
curl http://localhost:9998/tika

# Restart Tika
docker-compose restart tika
```

### Database Issues

```bash
# Reset database (WARNING: deletes all logs)
rm email_interceptor.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Port Already in Use

Change ports in `.env`:
```env
PROXY_PORT=2526
FLASK_PORT=5001
```

## Security Considerations

- Change `SECRET_KEY` in production
- Use HTTPS for Flask UI in production
- Restrict access to web dashboard
- Review quarantined emails regularly
- Monitor logs for bypass attempts

## License

This project is provided as-is for educational and research purposes.

## Contributing

Contributions welcome! Areas for improvement:
- Additional detection patterns
- Machine learning-based detection
- Performance optimization
- Enhanced UI features
- Integration with SIEM systems


# Project Structure

## Directory Layout

```
mailguard/
├── mailguard/                  # Main Python package
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── engines/               # Processing engines
│   │   ├── __init__.py
│   │   ├── detection_engine.py    # Pattern detection (regex)
│   │   ├── content_extractor.py   # Apache Tika integration
│   │   └── policy_engine.py       # Policy enforcement
│   ├── models/                # Database models
│   │   ├── __init__.py
│   │   ├── email.py          # EmailLog model
│   │   ├── recipient.py      # EmailRecipient model
│   │   └── attachment.py     # EmailAttachment model
│   └── proxy/                 # SMTP proxy
│       ├── __init__.py
│       └── smtp_proxy.py     # SMTP proxy handler
│
├── app.py                     # Flask web application
├── main.py                    # Main entry point
├── test_email.py              # Test email sender script
│
├── static/                    # Static web assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
│
├── templates/                 # HTML templates
│   └── index.html
│
├── test_emails/               # Test email samples
│   ├── README.md
│   └── *.txt                  # Various test scenarios
│
├── instance/                  # Database files (gitignored)
├── quarantine/                # Quarantined emails (gitignored)
│
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Apache Tika setup
├── setup.sh                   # Automated setup script
└── .env                       # Environment config (gitignored)
```

## Package Organization

### `mailguard/engines/`
Main processing code:
- `detection_engine.py`: Finds sensitive patterns (credit cards, SIN, SSN, emails)
- `content_extractor.py`: Pulls text from attachments using Apache Tika
- `policy_engine.py`: Applies policies (block, sanitize, quarantine, tag)

### `mailguard/models/`
Database models (SQLAlchemy):
- `email.py`: Main `EmailLog` model and database instance
- `recipient.py`: `EmailRecipient` model (one-to-many with EmailLog)
- `attachment.py`: `EmailAttachment` model (one-to-many with EmailLog)

### `mailguard/proxy/`
SMTP proxy code:
- `smtp_proxy.py`: Handles SMTP using aiosmtpd, processes emails and applies policies

### Root Level
- `app.py`: Flask web app with API endpoints
- `main.py`: Starts the SMTP proxy and Flask UI
- `test_email.py`: Script to send test emails

## Import Examples

```python
# From root level scripts
from mailguard.config import Config
from mailguard.engines import DetectionEngine, PolicyEngine
from mailguard.proxy import SMTPProxy
from mailguard.models import db, EmailLog

# Within package (relative imports)
from ..config import Config
from ..engines import DetectionEngine
from ..models import db
```

## Design Notes

- Each model in its own file to keep things organized
- Engines folder groups the processing logic together
- Proxy folder keeps SMTP handling separate
- CSS and JS are in separate files from HTML
- Test emails are in their own folder

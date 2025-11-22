# Project Structure

## Directory Layout

```
email_interceptor/
├── email_interceptor/          # Main Python package
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

### `email_interceptor/engines/`
Core processing logic:
- **detection_engine.py**: Detects sensitive patterns (credit cards, SIN, SSN, emails)
- **content_extractor.py**: Extracts text from attachments using Apache Tika
- **policy_engine.py**: Enforces policies (block, sanitize, quarantine, tag)

### `email_interceptor/models/`
Database models using SQLAlchemy:
- **email.py**: Main `EmailLog` model and database instance
- **recipient.py**: `EmailRecipient` model (one-to-many with EmailLog)
- **attachment.py**: `EmailAttachment` model (one-to-many with EmailLog)

### `email_interceptor/proxy/`
SMTP proxy implementation:
- **smtp_proxy.py**: SMTP handler using aiosmtpd, processes emails and applies policies

### Root Level
- **app.py**: Flask web application with API endpoints
- **main.py**: Starts both SMTP proxy and Flask UI
- **test_email.py**: Interactive script to send test emails

## Import Examples

```python
# From root level scripts
from email_interceptor.config import Config
from email_interceptor.engines import DetectionEngine, PolicyEngine
from email_interceptor.proxy import SMTPProxy
from email_interceptor.models import db, EmailLog

# Within package (relative imports)
from ..config import Config
from ..engines import DetectionEngine
from ..models import db
```

## Key Design Decisions

1. **Separate models**: Each model in its own file for clarity
2. **Engines folder**: Groups related processing logic
3. **Proxy folder**: Isolates SMTP handling code
4. **Static assets**: CSS and JS separated from HTML
5. **Test emails**: Organized in dedicated folder

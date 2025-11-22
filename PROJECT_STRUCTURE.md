# Project Structure

## Overview

The project has been structured for better organization and maintainability.

## Directory Structure

```
email_interceptor/
├── email_interceptor/          # Main package
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration management
│   ├── models.py              # Database models
│   ├── detection_engine.py    # Pattern detection logic
│   ├── content_extractor.py   # Tika integration
│   ├── policy_engine.py       # Policy enforcement
│   └── smtp_proxy.py          # SMTP proxy server
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css          # Stylesheet
│   └── js/
│       └── dashboard.js       # Dashboard JavaScript
│
├── templates/                  # HTML templates
│   └── index.html             # Dashboard template
│
├── app.py                     # Flask application
├── main.py                    # Entry point
├── demo.py                    # Demo script
├── test_email.py              # Test script
│
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Tika server setup
├── setup.sh                   # Setup script
│
└── Documentation/
    ├── README.md
    ├── QUICKSTART.md
    ├── TESTING.md
    └── TROUBLESHOOTING.md
```

## Package Organization

### `email_interceptor/` Package
Contains all core modules:
- **config.py**: Configuration management using environment variables
- **models.py**: SQLAlchemy database models
- **detection_engine.py**: Regex and spaCy-based pattern detection
- **content_extractor.py**: Apache Tika integration for content extraction
- **policy_engine.py**: Policy enforcement (block, sanitize, quarantine, tag)
- **smtp_proxy.py**: SMTP proxy server using aiosmtpd

### Root Level Files
- **app.py**: Flask web application with API endpoints
- **main.py**: Main entry point that starts both proxy and UI
- **demo.py**: Standalone demo script for testing detection
- **test_email.py**: Script to send test emails through proxy

### Static Files
- **static/css/style.css**: All CSS styles (separated from HTML)
- **static/js/dashboard.js**: All JavaScript functionality (separated from HTML)

### Templates
- **templates/index.html**: Clean HTML template that references external CSS/JS

## Benefits of This Structure

1. **Separation of Concerns**: Core logic in package, web app at root
2. **Cleaner HTML**: CSS and JS in separate files
3. **Better Organization**: Related modules grouped together
4. **Easier Maintenance**: Clear structure makes it easy to find files
5. **Scalability**: Easy to add new modules or features

## Import Examples

```python
# From root level scripts
from email_interceptor.config import Config
from email_interceptor.detection_engine import DetectionEngine

# Within package (relative imports)
from .config import Config
from .detection_engine import DetectionEngine
```

## Running the Project

The structure doesn't change how you run the project:

```bash
python main.py          # Start the interceptor
python demo.py          # Run demo
python test_email.py    # Send test email
```


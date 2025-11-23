# Project Structure

This document describes the project structure.

## Directory Layout

```
mailguard/
├── mailguard-server/              # Server-side code (Python)
│   ├── mailguard/                 # MailGuard package
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration settings
│   │   ├── api/                   # Flask API
│   │   │   ├── __init__.py
│   │   │   ├── app.py             # Flask app factory
│   │   │   └── routes/            # API route handlers
│   │   │       ├── __init__.py
│   │   │       ├── emails.py      # Email endpoints
│   │   │       ├── attachments.py # Attachment endpoints
│   │   │       ├── events.py      # SSE event streaming
│   │   │       └── stats.py       # Statistics endpoints
│   │   ├── engines/               # Processing engines
│   │   │   ├── __init__.py
│   │   │   ├── content_extractor.py  # Tika content extraction
│   │   │   ├── detection/         # Detection engine
│   │   │   │   ├── __init__.py
│   │   │   │   ├── engine.py      # Main detection engine
│   │   │   │   └── detectors/     # Detection implementations
│   │   │   │       ├── __init__.py
│   │   │   │       ├── presidio_detector.py  # ML-based Presidio
│   │   │   │       └── regex_detector.py     # Regex patterns
│   │   │   └── policy/            # Policy enforcement
│   │   │       ├── __init__.py
│   │   │       └── engine.py      # Policy decision engine
│   │   ├── models/                # Database models
│   │   │   ├── __init__.py
│   │   │   ├── email.py           # EmailLog model
│   │   │   ├── attachment.py      # EmailAttachment model
│   │   │   ├── recipient.py       # EmailRecipient model
│   │   │   ├── detection_result.py # DetectionResult dataclass
│   │   │   └── policy_decision.py  # PolicyDecision dataclass
│   │   ├── proxy/                 # SMTP proxy server
│   │   │   ├── __init__.py
│   │   │   └── smtp_proxy.py      # SMTP proxy controller
│   │   └── services/              # Business logic services
│   │       ├── __init__.py
│   │       ├── database/          # Database operations
│   │       │   ├── __init__.py
│   │       │   └── repository.py  # Email repository
│   │       ├── email/             # Email processing
│   │       │   ├── __init__.py
│   │       │   └── processor.py   # Email processor
│   │       ├── notifications/     # Event notifications
│   │       │   ├── __init__.py
│   │       │   └── notifier.py    # SSE notifier
│   │       ├── smtp/              # SMTP operations
│   │       │   ├── __init__.py
│   │       │   └── forwarder.py   # SMTP forwarder
│   │       └── storage/           # File storage
│   │           ├── __init__.py
│   │           ├── attachment.py  # Attachment storage
│   │           └── quarantine.py  # Quarantine storage
│   ├── app.py                     # Legacy Flask app (deprecated)
│   ├── main.py                    # Main entry point (starts proxy + Flask)
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Docker image definition
│   ├── scripts/                   # Utility scripts
│   │   ├── test_email.py          # Email testing script
│   │   └── fixtures/              # Test email fixtures
│   │       ├── README.md
│   │       └── *.txt              # Test email files
│   ├── instance/                  # Database files (mounted as volume)
│   │   └── mailguard.db           # SQLite database
│   ├── attachments/               # Stored email attachments (mounted as volume)
│   └── quarantine/                # Quarantined emails (mounted as volume)
│
├── mailguard-client/              # MailGuard Dashboard (React)
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── EmailTable.jsx     # Email list table
│   │   │   ├── Filters.jsx        # Filter controls
│   │   │   ├── Header.jsx         # Dashboard header
│   │   │   └── StatsGrid.jsx      # Statistics display
│   │   ├── App.jsx                # Main app component
│   │   ├── main.jsx               # Entry point
│   │   └── index.css              # Global styles
│   ├── index.html                 # HTML template
│   ├── Dockerfile                 # Docker image definition
│   ├── package.json
│   └── vite.config.js
│
├── smtp-client/                   # Email Client Application (React)
│   ├── src/
│   │   ├── components/            # Email client components
│   │   │   ├── ComposeEmail.jsx   # Email composer
│   │   │   ├── ComposeEmail.css
│   │   │   ├── EmailList.jsx      # Email inbox list
│   │   │   ├── EmailList.css
│   │   │   ├── EmailView.jsx      # Email detail view
│   │   │   ├── EmailView.css
│   │   │   ├── Sidebar.jsx        # Navigation sidebar
│   │   │   ├── Sidebar.css
│   │   │   ├── Toast.jsx          # Toast notifications
│   │   │   └── Toast.css
│   │   ├── App.jsx                # Main app component
│   │   ├── App.css                # App styles
│   │   ├── main.jsx               # Entry point
│   │   ├── index.css              # Global styles
│   │   └── config.js              # Configuration
│   ├── index.html                 # HTML template
│   ├── Dockerfile                 # Docker image definition
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml             # Docker Compose orchestration (all services)
├── README.md                      # Main project documentation
├── PROJECT_STRUCTURE.md           # This file
└── TROUBLESHOOTING.md             # Troubleshooting guide
```

## Applications

### 1. MailGuard Server (`mailguard-server/`)
- **Purpose**: SMTP proxy that intercepts and processes emails
- **Ports**: 
  - SMTP Proxy: 2525
  - Flask API: 5001
- **Technology**: Python, Flask, SQLAlchemy
- **Container**: `mailguard-server`

### 2. MailGuard Dashboard (`mailguard-client/`)
- **Purpose**: Admin dashboard to view intercepted emails and stats
- **Port**: 3000
- **Technology**: React, Vite
- **Access**: `http://localhost:3000`
- **Container**: `mailguard-dashboard`

### 3. SMTP Email Client (`smtp-client/`)
- **Purpose**: Email client for users to send/receive emails
- **Port**: 3001
- **Technology**: React, Vite
- **Access**: `http://localhost:3001`
- **Container**: `smtp-email-client`

### 4. Apache Tika (`tika`)
- **Purpose**: Content extraction from attachments
- **Port**: 9998
- **Container**: `mailguard-tika`

## Running the Project

### Quick Start with Docker

```bash
docker-compose up --build
```

This will:
- Build all Docker images
- Start all services (Tika, Server, Dashboard, Email Client)
- Set up networking between services
- Persist data in volumes

**Access the services:**
- SMTP Proxy: `localhost:2525`
- Flask API: `http://localhost:5001`
- Dashboard: `http://localhost:3000`
- Email Client: `http://localhost:3001`

**Stop all services:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Start without rebuilding (if images already exist):**
```bash
docker-compose up
```

No need to rebuild if you haven't changed anything.

## API Endpoints

All endpoints are prefixed with `/api`:

**Email Endpoints:**
- `GET /api/emails` - Get email logs (with pagination/filters)
- `GET /api/emails/<id>` - Get specific email details

**Statistics Endpoints:**
- `GET /api/stats` - Get statistics about intercepted emails
- `GET /api/stats/sse-clients` - Get count of connected SSE clients
- `POST /api/stats/test-sse` - Test endpoint to manually trigger SSE event

**Event Streaming:**
- `GET /api/events/stream` - Server-Sent Events stream for real-time updates

**Attachment Endpoints:**
- `GET /api/attachments/<id>/download` - Download email attachment

**Email Sending:**
- `POST /api/send-email` - Send email via SMTP proxy

## Server-Sent Events (SSE)

- `new_email` - Emitted when a new email is processed (real-time updates)

## Data Flow

1. **User sends email** (smtp-client) → Flask API → SMTP Proxy (2525)
2. **SMTP Proxy** intercepts → Processes → Logs to database
3. **Dashboard** (mailguard-client) reads from database via API
4. **Email Client** (smtp-client) reads from database via API

## Notes

- All services run as Docker containers orchestrated by `docker-compose.yml`
- Both React apps proxy API requests to Flask (port 5001)
- The SMTP proxy intercepts all emails sent through it
- All emails are logged to the same SQLite database
- CORS is enabled on Flask to allow both React apps to access APIs
- Email attachments are stored in `mailguard-server/attachments/` (persisted via Docker volume)
- Database and attachments are persisted via Docker volumes
- Services communicate via Docker's internal network
- Hot reload is enabled for development (source code mounted as volumes)

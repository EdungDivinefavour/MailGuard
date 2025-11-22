# Project Structure

This document describes the project structure.

## Directory Layout

```
email_interceptor/
├── mailguard-server/      # Server-side code (Python)
│   ├── mailguard/         # MailGuard package
│   │   ├── config.py      # Configuration
│   │   ├── engines/       # Detection, extraction, policy engines
│   │   ├── models/        # Database models
│   │   └── proxy/         # SMTP proxy server
│   ├── app.py             # Flask API server
│   ├── main.py            # Main entry point (starts proxy + Flask)
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Docker image definition
│   ├── test_email.py      # Test script
│   ├── instance/          # Database files (mounted as volume)
│   ├── attachments/       # Stored email attachments (mounted as volume)
│   ├── quarantine/        # Quarantined emails (mounted as volume)
│   └── test_emails/       # Test email files
│
├── mailguard-client/       # MailGuard Dashboard (React)
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.jsx        # Main app
│   │   └── main.jsx       # Entry point
│   ├── Dockerfile         # Docker image definition
│   ├── package.json
│   └── vite.config.js
│
├── smtp-client/           # Email Client Application (React)
│   ├── src/
│   │   ├── components/    # Email client components
│   │   ├── App.jsx        # Main app
│   │   └── main.jsx       # Entry point
│   ├── Dockerfile         # Docker image definition
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml     # Docker Compose orchestration (all services)
└── .dockerignore          # Files to exclude from Docker builds
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

## API Endpoints

All endpoints are prefixed with `/api`:

- `GET /api/emails` - Get email logs (with pagination/filters)
- `GET /api/emails/<id>` - Get specific email details
- `GET /api/stats` - Get statistics
- `POST /api/send-email` - Send email via SMTP proxy
- `GET /api/attachments/<id>/download` - Download email attachment

## WebSocket Events

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

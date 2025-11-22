# Project Structure

This document describes the reorganized project structure.

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
│   ├── setup.sh           # Setup script (venv, deps, Tika)
│   ├── test_email.py      # Test script
│   ├── docker-compose.yml # Docker config for Tika
│   ├── instance/          # Database files
│   ├── attachments/       # Stored email attachments
│   ├── quarantine/        # Quarantined emails
│   └── test_emails/       # Test email files
│
├── mailguard-client/       # MailGuard Dashboard (React)
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.jsx        # Main app
│   │   └── main.jsx       # Entry point
│   ├── setup.sh           # Setup script (npm install)
│   ├── package.json
│   └── vite.config.js
│
├── smtp-client/           # Email Client Application (React)
│   ├── src/
│   │   ├── components/    # Email client components
│   │   ├── App.jsx        # Main app
│   │   └── main.jsx       # Entry point
│   ├── setup.sh           # Setup script (npm install)
│   ├── package.json
│   └── vite.config.js
│
├── start.sh               # Main startup script (sets up and starts all services)
└── start.ps1              # Windows startup script
```

## Applications

### 1. MailGuard Server (`mailguard-server/`)
- **Purpose**: SMTP proxy that intercepts and processes emails
- **Ports**: 
  - SMTP Proxy: 2525
  - Flask API: 5001
- **Technology**: Python, Flask, SQLAlchemy
- **Location**: All server code is in `mailguard-server/` directory

### 2. MailGuard Dashboard (`mailguard-client/`)
- **Purpose**: Admin dashboard to view intercepted emails and stats
- **Port**: 3000
- **Technology**: React, Vite
- **Access**: `http://localhost:3000`

### 3. SMTP Email Client (`smtp-client/`)
- **Purpose**: Email client for users to send/receive emails
- **Port**: 3001
- **Technology**: React, Vite
- **Access**: `http://localhost:3001`

## Running the Project

### Quick Start (All Services)
```bash
./start.sh
```
This will:
- Set up all three projects (if needed)
- Start all services
- Show server logs in the current terminal

### Manual Setup and Start

#### 1. Setup and Start Server
```bash
cd mailguard-server
./setup.sh          # First time setup
source .venv/bin/activate
python main.py
```
This starts:
- SMTP proxy on port 2525
- Flask API on port 5001

#### 2. Setup and Start MailGuard Dashboard
```bash
cd mailguard-client
./setup.sh          # First time setup
npm run dev
```
Access at: `http://localhost:3000`

#### 3. Setup and Start Email Client
```bash
cd smtp-client
./setup.sh          # First time setup
npm run dev
```
Access at: `http://localhost:3001`

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

- Both React apps proxy API requests to Flask (port 5001)
- The SMTP proxy intercepts all emails sent through it
- All emails are logged to the same SQLite database
- CORS is enabled on Flask to allow both React apps to access APIs
- Email attachments are stored in `mailguard-server/attachments/`
- Each project has its own `setup.sh` script for easy setup
- The main `start.sh` script orchestrates setup and startup of all services

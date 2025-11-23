# Troubleshooting Guide

## Common Issues and Solutions

### Docker/Tika Not Available

**Error**: `docker-compose: command not found`

**Solution**: 
1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Start Docker
3. Run: `cd mailguard-server && docker-compose up -d`

You can test without Tika for basic email body detection, but you'll need it for attachment extraction.

### Port Already in Use

**Error**: `Address already in use` on port 2525 or 5001

**Solution**: Change ports in `.env`:
```env
PROXY_PORT=2526
FLASK_PORT=5001
```

### Database Errors

**Error**: `OperationalError` or database locked

**Solution**: Reset the database (warning: this deletes all logs):
```bash
cd mailguard-server
rm instance/mailguard.db
source .venv/bin/activate
python main.py  # Creates a new database
```

### SMTP Connection Fails

**Error**: `Connection refused` or `SMTP send failed`

**Solution**:
1. Check `UPSTREAM_SMTP_HOST` and `UPSTREAM_SMTP_PORT` in `.env`
2. Verify your SMTP server is accessible
3. For Gmail, use:
   ```env
   UPSTREAM_SMTP_HOST=smtp.gmail.com
   UPSTREAM_SMTP_PORT=587
   ```
4. Test connection: `telnet smtp.gmail.com 587`

### No Detections Found

**Issue**: Emails with sensitive data not being flagged

**Solution**:
1. Check confidence threshold in `.env`: `MIN_CONFIDENCE=0.7`
2. Lower threshold: `MIN_CONFIDENCE=0.5`
3. Verify patterns in test email match expected formats:
   - Credit card: `4532-1234-5678-9010` (16 digits with dashes)
   - SIN: `123-456-789` (9 digits with dashes)
   - SSN: `123-45-6789` (9 digits with dashes)

### Dashboard Not Loading

**Error**: Cannot access `http://localhost:5001`

**Solution**:
1. Check if Flask is running (should see in terminal output)
2. Check port: `lsof -i :5001`
3. Try: `http://127.0.0.1:5001`
4. Check firewall settings

### Import Errors

**Error**: `ModuleNotFoundError` or `ImportError`

**Solution**:
```bash
cd mailguard-server
# Re-run setup script
./setup.sh

# Or manually:
source .venv/bin/activate
pip install -r requirements.txt
```

### Virtual Environment Issues

**Error**: `venv/bin/activate: No such file or directory`

**Solution**:
```bash
cd mailguard-server
# Re-run setup script (it will recreate venv if needed)
./setup.sh

# Or manually:
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Getting Help

Something else broken? Try these:

1. Check the logs: `mailguard.log`
2. Send a test email: `python test_email.py`
3. Make sure everything's actually running:
   - Tika: `curl http://localhost:9998/tika`
   - Proxy: check terminal output
   - Flask: check terminal output

## Quick Health Check

Run these to verify everything's set up:

```bash
# Check Python
python3 --version

# Check Node.js
node --version
npm --version

# Check virtual environment
cd mailguard-server
source .venv/bin/activate
which python

# Check dependencies
pip list | grep -E "flask|aiosmtpd"

# Check Tika
curl http://localhost:9998/tika

# Test email sending
python test_email.py
```

## Setup Scripts

Each project has its own `setup.sh` script:
- `mailguard-server/setup.sh` - Sets up Python venv, dependencies, .env, and Tika
- `mailguard-client/setup.sh` - Installs npm dependencies
- `smtp-client/setup.sh` - Installs npm dependencies

Run `./start.sh` from the root directory to set up and start everything automatically.


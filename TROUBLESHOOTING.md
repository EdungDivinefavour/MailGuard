# Troubleshooting Guide

## Common Issues and Solutions

### spaCy Model Installation Fails

**Error**: `HTTP error 404` or `Could not install requirement`

**Solution**: spaCy is optional! The system works fine without it.

1. **Skip spaCy installation**: When prompted during setup, choose 'n'
2. **Disable spaCy in config**: Set `ENABLE_SPACY=false` in `.env`
3. **Install manually later** (if needed):
   ```bash
   source .venv/bin/activate
   python -m spacy download en_core_web_sm
   ```

The regex-based detection (credit cards, SIN, SSN, emails) works without spaCy.

### Docker/Tika Not Available

**Error**: `docker-compose: command not found`

**Solution**: 
1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Start Docker
3. Run: `docker-compose up -d`

**Alternative**: You can test the system without Tika for basic email body detection. Attachment extraction requires Tika.

### Port Already in Use

**Error**: `Address already in use` on port 2525 or 5001

**Solution**: Change ports in `.env`:
```env
PROXY_PORT=2526
FLASK_PORT=5001
```

### Database Errors

**Error**: `OperationalError` or database locked

**Solution**:
```bash
# Reset database (WARNING: deletes all logs)
rm instance/email_interceptor.db
python main.py  # Will recreate database automatically
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
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Virtual Environment Issues

**Error**: `venv/bin/activate: No such file or directory`

**Solution**:
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Getting Help

If you encounter other issues:

1. Check the logs: `email_interceptor.log`
2. Send test email: `python test_email.py`
3. Verify all services are running:
   - Tika: `curl http://localhost:9998/tika`
   - Proxy: Check terminal output
   - Flask: Check terminal output

## Quick Health Check

Run these commands to verify everything is set up:

```bash
# Check Python
python3 --version

# Check virtual environment
source .venv/bin/activate
which python

# Check dependencies
pip list | grep -E "flask|aiosmtpd"

# Check Tika
curl http://localhost:9998/tika

# Test email sending
python test_email.py
```


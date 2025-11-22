# Quick Start Guide - Email Interceptor

## Step 1: Initial Setup

### Option A: Automated Setup (Recommended)
```bash
./setup.sh
```

### Option B: Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install spaCy model (optional but recommended)
python -m spacy download en_core_web_sm

# 4. Start Apache Tika server
docker-compose up -d

# 5. Create .env file (see Step 2)
```

## Step 2: Configure Environment

Create a `.env` file in the project root:

```bash
cat > .env << 'EOF'
# SMTP Proxy Configuration
PROXY_HOST=0.0.0.0
PROXY_PORT=2525
UPSTREAM_SMTP_HOST=smtp.gmail.com
UPSTREAM_SMTP_PORT=587

# Apache Tika Configuration
TIKA_SERVER_URL=http://localhost:9998

# Flask UI Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=False
SECRET_KEY=dev-secret-key-change-in-production

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
EOF
```

**Important**: Update `UPSTREAM_SMTP_HOST` and `UPSTREAM_SMTP_PORT` with your actual SMTP server settings.

## Step 3: Start the Email Interceptor

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Start the interceptor
python main.py
```

You should see output like:
```
Starting Email Interceptor
Configuration: tag policy, Tika: http://localhost:9998
Starting SMTP proxy on 0.0.0.0:2525
Forwarding to smtp.gmail.com:587
Flask UI starting on http://0.0.0.0:5001
Email Interceptor is running. Press Ctrl+C to stop.
```

## Step 4: Access the Web Dashboard

Open your browser and go to:
```
http://localhost:5001
```

You'll see the dashboard with statistics and email logs.

## Step 5: Test the System

### Test 1: Send Email with Sensitive Data

In a **new terminal** (keep the interceptor running):

```bash
# Activate virtual environment
source .venv/bin/activate

# Send test email with sensitive data
python test_email.py --type sensitive
```

This will send an email containing:
- Credit card: 4532-1234-5678-9010
- SIN: 123-456-789
- Email address
- Phone number
- IP address

### Test 2: Send Benign Email

```bash
python test_email.py --type benign
```

This sends a regular email without sensitive data.

### Test 3: Check the Dashboard

1. Go to `http://localhost:5001`
2. You should see:
   - Statistics updated (total emails, flagged, etc.)
   - The test email in the logs
   - Detection results showing what was found
   - Policy applied (tag, block, etc.)

### Test 4: Run Demo Script

Test detection engine directly:

```bash
python demo.py
```

This will show detection results for various test cases.

## Step 6: Configure Your Mail Client

To use the proxy with a real mail client:

1. **Configure your mail client** to use:
   - SMTP Server: `localhost` (or your server IP)
   - SMTP Port: `2525`
   - Authentication: Same as your normal SMTP settings

2. **Send an email** through your mail client

3. **Check the dashboard** to see if it was intercepted and analyzed

## Troubleshooting

### Tika Server Not Running

```bash
# Check if Tika is running
docker ps | grep tika

# Start Tika if not running
docker-compose up -d

# Check Tika health
curl http://localhost:9998/tika
```

### Port Already in Use

If port 2525 or 5001 is already in use, change them in `.env`:
```env
PROXY_PORT=2526
FLASK_PORT=5001
```

### Database Issues

```bash
# Reset database (WARNING: deletes all logs)
rm email_interceptor.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### SMTP Connection Issues

If you can't connect to the upstream SMTP server:
1. Check `UPSTREAM_SMTP_HOST` and `UPSTREAM_SMTP_PORT` in `.env`
2. Verify your network connection
3. Check firewall settings
4. For Gmail, you may need to use port 587 with TLS

## Example Workflow

1. **Start the interceptor**: `python main.py`
2. **Open dashboard**: `http://localhost:5001`
3. **Send test email**: `python test_email.py --type sensitive`
4. **View results** in the dashboard:
   - See the email in the logs
   - Check detection results
   - View applied policy
   - See processing time
5. **Filter emails**: Use the dashboard filters to see only flagged emails
6. **Check statistics**: View overall stats and policy breakdown

## Next Steps

- Customize detection patterns in `detection_engine.py`
- Adjust policy rules in `policy_engine.py`
- Configure your mail server to route through the proxy
- Set up monitoring and alerts
- Review quarantined emails in the `quarantine/` directory


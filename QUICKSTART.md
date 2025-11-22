# Quick Start Guide

Get MailGuard running in 5 minutes.

## Step 1: Setup

```bash
./setup.sh
```

This handles everything: virtual environment, dependencies, Tika server, and configuration.

## Step 2: Start MailGuard

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start MailGuard
python main.py
```

You should see:
```
✓ SMTP Proxy is listening on port 2525
✓ Ready to intercept emails...
Flask UI starting on http://0.0.0.0:5001
MailGuard is running. Press Ctrl+C to stop.
```

## Step 3: Test It

In a **new terminal** (keep the interceptor running):

```bash
source .venv/bin/activate
python test_email.py
```

Choose an option from the menu (e.g., option 2 for credit card test).

## Step 4: View Results

Open your browser to: `http://localhost:5001`

You'll see:
- Statistics (total emails, flagged, blocked)
- Email logs with detection results
- Policy actions applied

## That's It!

The system is now intercepting and analyzing emails. Send more test emails or configure your mail client to use `localhost:2525` as the SMTP server.

## Next Steps

- **Configure your mail client**: Point SMTP to `localhost:2525`
- **Customize policies**: Edit `mailguard/engines/policy_engine.py`
- **Add detection patterns**: Edit `mailguard/engines/detection_engine.py`
- **Review logs**: Check the dashboard regularly

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for help with common issues.

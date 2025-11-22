# Quick Start Guide

Get MailGuard running in a few minutes.

## Step 1: Setup

```bash
./setup.sh
```

Creates the virtual environment, installs dependencies, starts Tika, and sets up the config.

## Step 2: Start MailGuard

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start MailGuard
python main.py
```

You should see something like:
```
✓ SMTP Proxy is listening on port 2525
✓ Ready to intercept emails...
Flask UI starting on http://0.0.0.0:5001
MailGuard is running. Press Ctrl+C to stop.
```

## Step 3: Test It

Open a new terminal (keep the first one running):

```bash
source .venv/bin/activate
python test_email.py
```

Pick an option from the menu. Option 2 tests credit card detection.

## Step 4: View Results

Open `http://localhost:5001` in your browser. You'll see stats, email logs, detection results, and what actions were taken.

## That's It!

MailGuard is now intercepting and checking emails. Try sending more test emails or point your mail client to `localhost:2525`.

## Next Steps

- Point your mail client's SMTP to `localhost:2525`
- Tweak policies in `mailguard/engines/policy_engine.py`
- Add detection patterns in `mailguard/engines/detection_engine.py`
- Check the dashboard for intercepted emails

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for help with common issues.

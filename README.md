# MailGuard - Email Security Proxy

MailGuard is an email security tool that sits between your email client and your email server. Think of it like a security guard that checks every email before it gets sent - it looks for sensitive information like credit card numbers, social security numbers, and other private data, then decides what to do with it.

## What Does It Do?

When you send an email, MailGuard:
1. **Intercepts it** before it reaches your email server
2. **Scans it** for sensitive information (credit cards, SSNs, etc.)
3. **Takes action** - it can block the email, remove the sensitive data, or just tag it with a warning
4. **Logs everything** so you can see what happened in a nice dashboard

## What You Need

Just Docker! That's it. If you don't have Docker installed, grab it from [docker.com](https://www.docker.com/products/docker-desktop).

## Getting Started

### Step 1: Build and start the containers

Open a terminal in the project folder and run:

```bash
docker-compose up --build
```

This will:
- Build all the Docker images (this might take a few minutes the first time)
- Start all the services (Tika, MailGuard Server, Dashboard, and Email Client)
- Show logs from all services in your terminal

**To see just the server logs:**
```bash
docker-compose up --build mailguard-server
```

Or to tail logs after everything is running:
```bash
docker-compose logs -f mailguard-server
```

**First time setup:** If you don't have a `.env` file, it will automatically create one from `.env.debug` with default settings. You can edit `.env` later if you need to change anything.

### Step 2: Open the Apps

Once everything is running, you'll see a bunch of logs in your terminal. When it's ready, open these in your browser:

- **Email Client** (where you send/receive emails): http://localhost:3001
- **Dashboard** (where you see all intercepted emails): http://localhost:3000
- **API** (for developers): http://localhost:5001

The SMTP proxy runs on port 2525 (you won't open this in a browser, but your email client will use it).

## How to Use It

### Sending Emails

1. Go to http://localhost:3001
2. Enter your email address when it asks
3. Click "Compose" to write a new email
4. Fill in who you're sending to, the subject, and your message
5. You can attach files if you want
6. Click "Send"

The email will go through MailGuard, get checked, and then be sent. You'll see a notification when it's sent successfully!

### Viewing Intercepted Emails

1. Go to http://localhost:3000
2. You'll see a dashboard with:
   - Statistics (how many emails, how many flagged, etc.)
   - A list of all emails that went through the system
   - Details about what sensitive data was found (if any)

Click on any email to see more details, including what was detected and what action was taken.

## Stopping Everything

When you're done, press `Ctrl+C` in the terminal where Docker is running. Or in a new terminal, run:

```bash
docker-compose down
```

This stops all the services cleanly.

## Viewing Logs

Want to see what's happening behind the scenes? Run:

```bash
docker-compose logs -f
```

This shows you all the logs from all services. Press `Ctrl+C` to stop watching.

## Configuration

### Changing Settings

The first time you run `docker-compose up --build`, it automatically creates a `.env` file from `.env.debug` if one doesn't exist. 

You can edit the `.env` file to change settings. Here are the important ones:

**Where to send emails:**
- `UPSTREAM_SMTP_HOST` - Your real email server (like `smtp.gmail.com` or `smtp.outlook.com`)
- `UPSTREAM_SMTP_PORT` - Usually `587` for Gmail/Outlook, or `25` for other servers

**What to do when sensitive data is found:**
- `DEFAULT_POLICY` - Set this to:
  - `tag` - Send the email but add warning headers (default - safest option)
  - `block` - Don't send the email at all (most secure)
  - `sanitize` - Remove the sensitive data and send the rest
  - `quarantine` - Save it to a folder instead of sending

**Detection settings:**
- `USE_PRESIDIO` - Set to `true` to use ML-based Presidio detection (default, recommended) or `false` to use regex-only
- `MIN_CONFIDENCE` - Minimum confidence threshold (0.0-1.0) for detections (default: 0.7)

**Other useful settings:**
- `PROXY_PORT` - Change if port 2525 is already in use
- `FLASK_PORT` - Change if port 5001 is already in use

After changing `.env`, restart the services:
```bash
docker-compose down
docker-compose up --build
```

## Testing It Out

Want to test if it's working? You can use the built-in test script:

```bash
docker-compose exec mailguard-server python test_email.py
```

You can send test emails with different types of sensitive data to see how MailGuard handles them.

## What Gets Detected?

MailGuard uses **Presidio** (Microsoft's ML-based PII detection library) to automatically scan for sensitive information. This provides more accurate detection than simple regex patterns.

MailGuard can detect:
- **Credit card numbers** - Like `4532-1234-5678-9010`
- **Social Security Numbers (SSN)** - Like `123-45-6789`
- **Canadian SIN numbers** - Like `123-456-789`
- **Email addresses** - Any email addresses in the content
- **Phone numbers** - Various formats
- **Bank account numbers** - US bank account numbers
- **IP addresses** - IPv4 and IPv6 addresses
- **Passport numbers** - US passport numbers
- **Driver's license numbers** - US driver's license numbers
- **Person names** - Detected through Named Entity Recognition
- **Organizations** - Company and organization names
- **Locations** - Geographic locations
- **Dates and times** - Sensitive date/time information

Each detection comes with a confidence score, so you can filter out false positives.

## Troubleshooting

### Port Already in Use

If you get an error about a port being used, either:
1. Stop whatever is using that port, or
2. Change the port in `docker-compose.yml` (look for the `ports:` section)

### Services Won't Start

Make sure Docker is running! On Mac/Windows, you need Docker Desktop to be open.

### Can't Access the Web Pages

Give it a minute or two to boot up. Check the logs with `docker-compose logs -f` if something's not working.

### Presidio/ML Detection Not Working

If you see warnings about Presidio not working:
1. If Presidio fails to initialize, the system will automatically fall back to regex-based detection
2. Check the logs with `docker-compose logs -f mailguard-server` to see what's happening

### Need to Start Fresh

If something gets messed up, you can reset everything:

```bash
docker-compose down
docker-compose up --build
```

This rebuilds everything from scratch.

## Project Structure

This project has three main parts:

1. **mailguard-server** - The brain. Handles email interception, scanning, and the API.
2. **mailguard-client** - The dashboard. Shows you all the emails and stats.
3. **smtp-client** - The email app. Where you actually write and send emails.

All three run as separate Docker containers, but they work together.

## Data Storage

Your data is saved in these folders (they're mounted as Docker volumes, so they persist even when containers restart):

- `mailguard-server/instance/` - The database with all email logs
- `mailguard-server/attachments/` - Any files attached to emails
- `mailguard-server/quarantine/` - Emails that were quarantined

## Need Help?

Check out [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more help, or look at the logs with `docker-compose logs -f` to see what's happening.

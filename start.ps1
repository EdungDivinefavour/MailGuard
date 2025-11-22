# PowerShell script for Windows users
# Start script for MailGuard - Sets up and starts all services

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   MailGuard - Startup Script          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$missing = @()

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    $missing += "Python 3"
}

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    $missing += "Node.js"
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    $missing += "npm"
}

if ($missing.Count -gt 0) {
    Write-Host "✗ Missing dependencies:" -ForegroundColor Red
    foreach ($dep in $missing) {
        Write-Host "  - $dep"
    }
    Write-Host ""
    Write-Host "Please install the missing dependencies and try again."
    exit 1
}

Write-Host "✓ All prerequisites found" -ForegroundColor Green
Write-Host ""

# Setup MailGuard Server
Write-Host "Setting up MailGuard Server..." -ForegroundColor Yellow
Set-Location "mailguard-server"

if (-not (Test-Path ".venv")) {
    Write-Host "  Creating virtual environment..."
    python -m venv .venv
}

Write-Host "  Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

if (-not (Test-Path ".env")) {
    Write-Host "  Running setup script..."
    & .\setup.sh
} else {
    Write-Host "  Installing/updating Python dependencies..."
    python -m pip install --upgrade pip -q
    pip install -r requirements.txt -q
}

Write-Host "✓ MailGuard Server setup complete" -ForegroundColor Green
Write-Host ""

# Setup MailGuard Client
Write-Host "Setting up MailGuard Client..." -ForegroundColor Yellow
Set-Location "..\mailguard-client"

if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing dependencies..."
    npm install --silent
} else {
    Write-Host "  Dependencies already installed"
}

Write-Host "✓ MailGuard Client setup complete" -ForegroundColor Green
Write-Host ""

# Setup SMTP Client
Write-Host "Setting up SMTP Client..." -ForegroundColor Yellow
Set-Location "..\smtp-client"

if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing dependencies..."
    npm install --silent
} else {
    Write-Host "  Dependencies already installed"
}

Write-Host "✓ SMTP Client setup complete" -ForegroundColor Green
Write-Host ""

# Start services
Write-Host "Starting all services..." -ForegroundColor Cyan
Write-Host ""

# Start MailGuard Server
Write-Host "Starting MailGuard Server..." -ForegroundColor Blue
Set-Location "$SCRIPT_DIR\mailguard-server"
& .\.venv\Scripts\Activate.ps1
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
Start-Sleep -Seconds 3

Write-Host "✓ Server started" -ForegroundColor Green
Write-Host "  - SMTP Proxy: localhost:2525"
Write-Host "  - Flask API: http://localhost:5001"
Write-Host ""

# Start MailGuard Dashboard
Write-Host "Starting MailGuard Dashboard..." -ForegroundColor Blue
Set-Location "$SCRIPT_DIR\mailguard-client"
Start-Process npm -ArgumentList "run", "dev" -WindowStyle Hidden

Write-Host "✓ Dashboard started" -ForegroundColor Green
Write-Host "  - URL: http://localhost:3000"
Write-Host ""

# Start SMTP Client
Write-Host "Starting SMTP Client..." -ForegroundColor Blue
Set-Location "$SCRIPT_DIR\smtp-client"
Start-Process npm -ArgumentList "run", "dev" -WindowStyle Hidden

Write-Host "✓ Email Client started" -ForegroundColor Green
Write-Host "  - URL: http://localhost:3001"
Write-Host ""

# Summary
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   All Services Started!                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  📧 SMTP Proxy:     localhost:2525"
Write-Host "  🔌 Flask API:      http://localhost:5001"
Write-Host "  📊 Dashboard:      http://localhost:3000"
Write-Host "  ✉️  Email Client:   http://localhost:3001"
Write-Host ""
Write-Host "Press any key to stop all services..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


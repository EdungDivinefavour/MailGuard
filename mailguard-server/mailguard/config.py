"""Config settings for MailGuard."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from workspace if it exists, otherwise from current directory
workspace_env = Path('/workspace/.env')
if workspace_env.exists():
    load_dotenv(workspace_env)
else:
    load_dotenv()

class Config:
    """App configuration."""
    
    # SMTP Proxy
    PROXY_HOST = os.getenv('PROXY_HOST', '0.0.0.0')
    PROXY_PORT = int(os.getenv('PROXY_PORT', 2525))
    UPSTREAM_SMTP_HOST = os.getenv('UPSTREAM_SMTP_HOST', 'smtp.example.com')
    UPSTREAM_SMTP_PORT = int(os.getenv('UPSTREAM_SMTP_PORT', 25))
    
    # Apache Tika
    TIKA_SERVER_URL = os.getenv('TIKA_SERVER_URL', 'http://localhost:9998')
    
    # Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///mailguard.db')
    
    # Policy
    DEFAULT_POLICY = os.getenv('DEFAULT_POLICY', 'tag')
    MAX_ATTACHMENT_SIZE_MB = int(os.getenv('MAX_ATTACHMENT_SIZE_MB', 50))
    MAX_ARCHIVE_DEPTH = int(os.getenv('MAX_ARCHIVE_DEPTH', 5))
    
    # Detection
    MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', 0.7))
    ENABLE_SPACY = os.getenv('ENABLE_SPACY', 'true').lower() == 'true'
    
    # Quarantine
    QUARANTINE_DIR = Path(os.getenv('QUARANTINE_DIR', './quarantine'))
    QUARANTINE_DIR.mkdir(exist_ok=True)
    
    # Attachments
    ATTACHMENTS_DIR = Path(os.getenv('ATTACHMENTS_DIR', './attachments'))
    ATTACHMENTS_DIR.mkdir(exist_ok=True)


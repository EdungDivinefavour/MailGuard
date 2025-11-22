"""Quarantine storage service."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from email.message import EmailMessage

from ...config import Config

logger = logging.getLogger(__name__)


class QuarantineStorage:
    """Handles saving quarantined emails to disk."""
    
    def __init__(self, quarantine_dir: Path = None):
        """Initialize quarantine storage."""
        self.quarantine_dir = quarantine_dir or Config.QUARANTINE_DIR
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, message: EmailMessage) -> Optional[str]:
        """
        Save email message to quarantine directory.
        
        Args:
            message: Email message to quarantine
            
        Returns:
            Quarantine file path if successful, None otherwise
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message_id = message.get('Message-ID', 'unknown').replace('<', '').replace('>', '')
        safe_message_id = "".join(c for c in message_id if c.isalnum() or c in ('-', '_'))[:50]
        quarantine_file = self.quarantine_dir / f"{timestamp}_{safe_message_id}.eml"
        
        try:
            with open(quarantine_file, 'wb') as f:
                f.write(message.as_bytes())
            return str(quarantine_file)
        except Exception as e:
            logger.error(f"Error quarantining message: {e}")
            return None


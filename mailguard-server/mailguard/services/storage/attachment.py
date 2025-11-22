"""Attachment storage service."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from ...config import Config

logger = logging.getLogger(__name__)


class AttachmentStorage:
    """Handles saving email attachments to disk."""
    
    def __init__(self, storage_dir: Path = None):
        """Initialize attachment storage."""
        self.storage_dir = storage_dir or Config.ATTACHMENTS_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, filename: str, payload: bytes) -> Optional[str]:
        """
        Save attachment to disk and return file path.
        
        Args:
            filename: Original filename
            payload: File content as bytes
            
        Returns:
            File path if successful, None otherwise
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))[:200]
        attachment_file = self.storage_dir / f"{timestamp}_{safe_filename}"
        
        try:
            with open(attachment_file, 'wb') as f:
                f.write(payload)
            return str(attachment_file)
        except Exception as e:
            logger.error(f"Error saving attachment {filename}: {e}")
            return None


"""Policy decision data class."""
from typing import List, Dict, Optional
from dataclasses import dataclass
from email.message import EmailMessage

@dataclass
class PolicyDecision:
    """Decision made by policy engine."""
    action: str  # block, sanitize, quarantine, tag
    reason: str
    detections: List[Dict]
    original_message: Optional[EmailMessage] = None
    modified_message: Optional[EmailMessage] = None
    quarantine_path: Optional[str] = None


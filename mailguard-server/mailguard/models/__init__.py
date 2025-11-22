"""Database models and data classes for MailGuard."""
# Import in order to ensure relationships are registered
from .email import db, EmailLog
from .recipient import EmailRecipient
from .attachment import EmailAttachment
from .detection_result import DetectionResult
from .policy_decision import PolicyDecision

__all__ = [
    'db', 
    'EmailLog', 
    'EmailRecipient', 
    'EmailAttachment',
    'DetectionResult',
    'PolicyDecision'
]


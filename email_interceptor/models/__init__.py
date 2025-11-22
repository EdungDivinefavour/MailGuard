"""Database models for email interceptor."""
# Import in order to ensure relationships are registered
from .email import db, EmailLog
from .recipient import EmailRecipient
from .attachment import EmailAttachment

__all__ = ['db', 'EmailLog', 'EmailRecipient', 'EmailAttachment']


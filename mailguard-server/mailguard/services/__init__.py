"""Services for MailGuard."""
from .storage import AttachmentStorage, QuarantineStorage
from .database import EmailRepository
from .smtp import SMTPForwarder
from .notifications import EmailNotifier
from .email import EmailProcessor

__all__ = [
    'AttachmentStorage',
    'QuarantineStorage',
    'EmailRepository',
    'SMTPForwarder',
    'EmailNotifier',
    'EmailProcessor'
]


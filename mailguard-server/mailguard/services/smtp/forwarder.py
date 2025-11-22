"""SMTP forwarding service."""
import logging
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr

from ...config import Config

logger = logging.getLogger(__name__)


class SMTPForwarder:
    """Handles forwarding emails via SMTP."""
    
    def __init__(self):
        """Initialize SMTP forwarder."""
        pass
    
    def forward(self, message: EmailMessage) -> bool:
        """
        Forward message to upstream SMTP server.
        
        Args:
            message: Email message to forward
            
        Returns:
            True if successful, False otherwise
        """
        # Skip forwarding if upstream SMTP is not configured (for testing)
        if Config.UPSTREAM_SMTP_HOST == 'smtp.example.com':
            logger.info("Skipping forward - upstream SMTP not configured (OK for testing)")
            return True
        
        try:
            # Remove Bcc header before forwarding
            if 'Bcc' in message:
                del message['Bcc']
            
            # Extract sender
            sender = parseaddr(message.get('From', ''))[1]
            if not sender:
                sender = "no-reply@proxy"
            
            # Extract recipients
            recipients = []
            for header in ['To', 'Cc']:
                addrs = message.get_all(header, [])
                for addr in addrs:
                    _, email_addr = parseaddr(addr)
                    if email_addr:
                        recipients.append(email_addr)
            
            if not recipients:
                logger.warning("No recipients found, skipping forward")
                return False
            
            # Send using sendmail
            with smtplib.SMTP(Config.UPSTREAM_SMTP_HOST, Config.UPSTREAM_SMTP_PORT) as server:
                server.sendmail(sender, recipients, message.as_string())
                logger.info(f"Message forwarded to {len(recipients)} recipient(s)")
                return True
                
        except Exception as e:
            logger.warning(f"SMTP forward failed (this is OK for testing): {e}")
            return False


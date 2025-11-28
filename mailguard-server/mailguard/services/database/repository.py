"""Database repository for email logs."""
import logging
import os
import sys
from typing import List, Optional
from email.message import EmailMessage

from ...models import db, EmailLog, EmailRecipient, EmailAttachment
from ...models import DetectionResult, PolicyDecision

logger = logging.getLogger(__name__)


class EmailRepository:
    """Repository for email log database operations."""
    
    def __init__(self, flask_app=None):
        """Initialize email repository.
        
        Args:
            flask_app: Flask application instance (for database context)
        """
        self.flask_app = flask_app
    
    def save(self, metadata: dict, body_text: str, detections: List[DetectionResult],
             policy_decision: PolicyDecision, attachment_data: list,
             attachment_count: int, processing_time: float) -> Optional[EmailLog]:
        """
        Save email log to database.
        
        Args:
            metadata: Email metadata (message_id, sender, recipients, subject)
            body_text: Email body text
            detections: List of detection results
            policy_decision: Policy decision
            attachment_data: List of (filename, file_path) tuples
            attachment_count: Number of attachments
            processing_time: Processing time in milliseconds
            
        Returns:
            EmailLog object if successful, None otherwise
        """
        ctx = None
        try:
            ctx = self._get_flask_context()
            
            # Determine proper status based on policy action and detections
            if policy_decision.action == 'block':
                status = 'blocked'
            elif policy_decision.action == 'quarantine':
                status = 'quarantined'
            elif len(detections) > 0:
                status = 'flagged'
            else:
                status = 'processed'
            
            email_log = EmailLog(
                message_id=metadata['message_id'],
                sender=metadata['sender'],
                subject=metadata['subject'],
                flagged=len(detections) > 0,
                policy_applied=policy_decision.action,
                detection_results=[d.__dict__ for d in detections] if detections else None,
                body_text=body_text[:10000],  # Limit size
                attachment_count=attachment_count,
                status=status,
                processing_time_ms=processing_time
            )
            
            for recipient in metadata['recipients']:
                recipient_obj = EmailRecipient(
                    email_address=recipient,
                    recipient_type='to'
                )
                email_log.recipients.append(recipient_obj)
            
            for filename, file_path in attachment_data:
                attachment_obj = EmailAttachment(
                    filename=filename,
                    file_path=file_path
                )
                email_log.attachments.append(attachment_obj)
            
            db.session.add(email_log)
            db.session.commit()
            logger.info(f"Email saved to database (ID: {email_log.id})")
            
            email_dict = email_log.to_dict()
            email_log._email_dict = email_dict
            
            return email_log
            
        except Exception as db_err:
            logger.error(f"Database error: {db_err}")
            return None
        finally:
            if ctx:
                ctx.pop()
    
    def save_error(self, message: EmailMessage, error: Exception, start_time: float) -> Optional[EmailLog]:
        """
        Save error log to database.
        
        Args:
            message: Email message that caused error
            error: Exception that occurred
            start_time: Start time of processing
            
        Returns:
            EmailLog object if successful, None otherwise
        """
        import time
        ctx = None
        try:
            ctx = self._get_flask_context()
            
            error_recipients = list(message.get_all('To', []))
            email_log = EmailLog(
                message_id=message.get('Message-ID', 'unknown'),
                sender=message.get('From', 'unknown'),
                subject=message.get('Subject', ''),
                status='error',
                error_message=str(error),
                processing_time_ms=(time.time() - start_time) * 1000
            )
            
            for recipient in error_recipients:
                recipient_obj = EmailRecipient(
                    email_address=recipient,
                    recipient_type='to'
                )
                email_log.recipients.append(recipient_obj)
            
            db.session.add(email_log)
            db.session.commit()
            return email_log
            
        except Exception as db_error:
            logger.error(f"Database error while saving error: {db_error}")
            return None
        finally:
            if ctx:
                ctx.pop()
    
    def _get_flask_context(self):
        """Get Flask application context for database operations."""
        from flask import has_app_context
        
        if has_app_context():
            return None
        
        if self.flask_app:
            ctx = self.flask_app.app_context()
            ctx.push()
            return ctx
        
        try:
            parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            from mailguard.api import create_app
            flask_app = create_app()
            ctx = flask_app.app_context()
            ctx.push()
            return ctx
        except Exception as e:
            logger.warning(f"Could not get app context: {e}")
            return None


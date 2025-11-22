"""Email log model."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class EmailLog(db.Model):
    """Stores intercepted email info."""
    __tablename__ = 'email_logs'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(255), unique=True, nullable=False)
    sender = Column(String(255), nullable=False)
    subject = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Detection results
    flagged = Column(Boolean, default=False, nullable=False)
    policy_applied = Column(String(50))  # block, sanitize, quarantine, tag
    detection_results = Column(JSON)  # List of detected patterns
    
    # Content info
    body_text = Column(Text)
    attachment_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default='pending')  # pending, processed, blocked, quarantined
    error_message = Column(Text)
    
    # Performance metrics
    processing_time_ms = Column(Float)
    
    # Relationships
    recipients = relationship('EmailRecipient', back_populates='email_log', cascade='all, delete-orphan')
    attachments = relationship('EmailAttachment', back_populates='email_log', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary."""
        try:
            recipients_list = []
            if hasattr(self, 'recipients') and self.recipients is not None:
                recipients_list = [r.email_address for r in self.recipients if hasattr(r, 'email_address')]
            
            attachments_list = []
            attachment_names_list = []
            if hasattr(self, 'attachments') and self.attachments is not None:
                attachments_list = [
                    {'id': a.id, 'filename': a.filename, 'file_path': a.file_path}
                    for a in self.attachments if hasattr(a, 'id') and hasattr(a, 'filename')
                ]
                attachment_names_list = [a.filename for a in self.attachments if hasattr(a, 'filename')]
            
            return {
                'id': self.id,
                'message_id': self.message_id,
                'sender': self.sender,
                'recipients': recipients_list,
                'subject': self.subject,
                'timestamp': self.timestamp.isoformat() if self.timestamp else None,
                'flagged': self.flagged,
                'policy_applied': self.policy_applied,
                'detection_results': self.detection_results,
                'body_text': self.body_text[:500] if self.body_text else None,
                'attachment_count': self.attachment_count,
                'attachment_names': attachment_names_list,
                'attachments': attachments_list,
                'status': self.status,
                'error_message': self.error_message,
                'processing_time_ms': self.processing_time_ms
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in to_dict for email {self.id}: {e}", exc_info=True)
            return {
                'id': self.id,
                'message_id': getattr(self, 'message_id', None),
                'sender': getattr(self, 'sender', None),
                'recipients': [],
                'subject': getattr(self, 'subject', None),
                'timestamp': self.timestamp.isoformat() if hasattr(self, 'timestamp') and self.timestamp else None,
                'flagged': getattr(self, 'flagged', False),
                'error': str(e)
            }


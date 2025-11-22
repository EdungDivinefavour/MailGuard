"""Database models for email interceptor."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class EmailLog(db.Model):
    """Model for storing intercepted email metadata."""
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
        return {
            'id': self.id,
            'message_id': self.message_id,
            'sender': self.sender,
            'recipients': [r.email_address for r in self.recipients],  # Always an array
            'subject': self.subject,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'flagged': self.flagged,
            'policy_applied': self.policy_applied,
            'detection_results': self.detection_results,
            'body_text': self.body_text[:500] if self.body_text else None,  # Truncate for display
            'attachment_count': self.attachment_count,
            'attachment_names': [a.filename for a in self.attachments],  # Always an array
            'status': self.status,
            'error_message': self.error_message,
            'processing_time_ms': self.processing_time_ms
        }


class EmailRecipient(db.Model):
    """Model for storing email recipients (one-to-many relationship)."""
    __tablename__ = 'email_recipients'
    
    id = Column(Integer, primary_key=True)
    email_log_id = Column(Integer, ForeignKey('email_logs.id'), nullable=False)
    email_address = Column(String(255), nullable=False)
    recipient_type = Column(String(10), default='to')  # to, cc, bcc
    
    # Relationship
    email_log = relationship('EmailLog', back_populates='recipients')


class EmailAttachment(db.Model):
    """Model for storing email attachment names (one-to-many relationship)."""
    __tablename__ = 'email_attachments'
    
    id = Column(Integer, primary_key=True)
    email_log_id = Column(Integer, ForeignKey('email_logs.id'), nullable=False)
    filename = Column(String(500), nullable=False)
    
    # Relationship
    email_log = relationship('EmailLog', back_populates='attachments')


"""Email attachment model."""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .email import db


class EmailAttachment(db.Model):
    """Model for storing email attachment names (one-to-many relationship)."""
    __tablename__ = 'email_attachments'
    
    id = Column(Integer, primary_key=True)
    email_log_id = Column(Integer, ForeignKey('email_logs.id'), nullable=False)
    filename = Column(String(500), nullable=False)
    
    # Relationship
    email_log = relationship('EmailLog', back_populates='attachments')


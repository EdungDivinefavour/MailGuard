"""Email recipient model."""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .email import db


class EmailRecipient(db.Model):
    """Stores email recipients (one-to-many with EmailLog)."""
    __tablename__ = 'email_recipients'
    
    id = Column(Integer, primary_key=True)
    email_log_id = Column(Integer, ForeignKey('email_logs.id'), nullable=False)
    email_address = Column(String(255), nullable=False)
    recipient_type = Column(String(10), default='to')  # to, cc, bcc
    
    # Relationship
    email_log = relationship('EmailLog', back_populates='recipients')


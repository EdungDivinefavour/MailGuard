"""SMTP proxy for intercepting and processing emails."""
import asyncio
import logging
import smtplib
import time
import tempfile
from email.message import EmailMessage
from email.utils import parseaddr
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message
from email.parser import BytesParser

from ..config import Config
from ..engines import DetectionEngine, ContentExtractor, PolicyEngine
from ..models import db, EmailLog, EmailRecipient, EmailAttachment

logger = logging.getLogger(__name__)

class EmailHandler(Message):
    """Handler for intercepted emails."""
    
    def __init__(self, detection_engine: DetectionEngine, 
                 content_extractor: ContentExtractor,
                 policy_engine: PolicyEngine):
        """Initialize email handler."""
        super().__init__()
        self.detection_engine = detection_engine
        self.content_extractor = content_extractor
        self.policy_engine = policy_engine
    
    def handle_message(self, message: EmailMessage):
        """Process intercepted email message (aiosmtpd handler method - synchronous)."""
        start_time = time.time()
        
        try:
            print(f"\n[DEBUG] handle_message called")
            print(f"[DEBUG] Message type: {type(message)}")
            print(f"[DEBUG] Message headers: {list(message.keys())}")
            
            # Extract message metadata
            message_id = message.get('Message-ID', f'<{time.time()}@proxy>')
            sender = message.get('From', 'unknown@unknown.com')
            recipients = message.get_all('To', []) + message.get_all('Cc', []) + message.get_all('Bcc', [])
            subject = message.get('Subject', '(no subject)')
            
            print(f"\n{'='*60}")
            print(f"📧 EMAIL INTERCEPTED")
            print(f"{'='*60}")
            print(f"From: {sender}")
            print(f"To: {', '.join(str(r) for r in recipients[:3])}")
            print(f"Subject: {subject}")
            logger.info(f"Email intercepted: {subject} from {sender}")
            
            # Extract body text
            body_text = self._extract_body_text(message)
            
            # Extract and process attachments
            attachment_texts = []
            attachment_names = []
            attachment_count = 0
            
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_disposition() == 'attachment':
                        attachment_count += 1
                        filename = part.get_filename()
                        if filename:
                            attachment_names.append(filename)
                            
                            # Save attachment temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix=filename) as tmp:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    tmp.write(payload)
                                    tmp_path = tmp.name
                                    
                                    # Extract text from attachment
                                    try:
                                        # Check if it's an archive
                                        import zipfile
                                        import tarfile
                                        
                                        if zipfile.is_zipfile(tmp_path) or tarfile.is_tarfile(tmp_path):
                                            extracted = self.content_extractor.extract_from_archive(
                                                tmp_path, 
                                                max_depth=Config.MAX_ARCHIVE_DEPTH
                                            )
                                            attachment_texts.extend(extracted.values())
                                        else:
                                            text = self.content_extractor.extract_text(
                                                tmp_path,
                                                max_size_mb=Config.MAX_ATTACHMENT_SIZE_MB
                                            )
                                            if text:
                                                attachment_texts.append(text)
                                    except Exception as e:
                                        logger.error(f"Error processing attachment {filename}: {e}")
                                    finally:
                                        try:
                                            import os
                                            os.unlink(tmp_path)
                                        except:
                                            pass
            
            # Combine all text for detection
            all_text = body_text
            if attachment_texts:
                all_text += "\n\n" + "\n\n".join(attachment_texts)
            
            # Run detection
            detections = self.detection_engine.detect_patterns(
                all_text,
                min_confidence=Config.MIN_CONFIDENCE
            )
            
            # Show detection results
            if detections:
                print(f"\n⚠️  SENSITIVE DATA DETECTED:")
                for det in detections:
                    print(f"   - {det.pattern_type}: '{det.matched_text}' (confidence: {det.confidence:.2f})")
            else:
                print(f"\n✓ No sensitive data detected")
            
            # Apply policy
            policy_decision = self.policy_engine.evaluate(detections, message)
            print(f"\n📋 Policy Decision: {policy_decision.action.upper()}")
            print(f"   Reason: {policy_decision.reason}")
            
            # Log to database
            processing_time = (time.time() - start_time) * 1000  # ms
            
            try:
                # Get Flask app context for database operations
                from flask import has_app_context
                ctx = None
                if not has_app_context():
                    # Import Flask app and create context
                    try:
                        import sys
                        import os
                        # Add parent directory to path to import app
                        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        if parent_dir not in sys.path:
                            sys.path.insert(0, parent_dir)
                        from app import app as flask_app
                        ctx = flask_app.app_context()
                        ctx.push()
                    except Exception as e:
                        logger.warning(f"Could not get app context: {e}")
                        ctx = None
                
                try:
                    email_log = EmailLog(
                        message_id=message_id,
                        sender=sender,
                        subject=subject,
                        flagged=len(detections) > 0,
                        policy_applied=policy_decision.action,
                        detection_results=[d.__dict__ for d in detections] if detections else None,
                        body_text=body_text[:10000],  # Limit size
                        attachment_count=attachment_count,
                        status='processed' if policy_decision.action != 'block' else 'blocked',
                        processing_time_ms=processing_time
                    )
                    
                    # Add recipients (always as array)
                    for recipient in recipients:
                        recipient_obj = EmailRecipient(
                            email_address=recipient,
                            recipient_type='to'  # Could be enhanced to track to/cc/bcc
                        )
                        email_log.recipients.append(recipient_obj)
                    
                    # Add attachment names (always as array)
                    for attachment_name in attachment_names:
                        attachment_obj = EmailAttachment(
                            filename=attachment_name
                        )
                        email_log.attachments.append(attachment_obj)
                    
                    db.session.add(email_log)
                    db.session.commit()
                    print(f"✓ Email logged to database (ID: {email_log.id})")
                    print(f"   View in dashboard: http://localhost:{Config.FLASK_PORT}")
                    print(f"{'='*60}\n")
                except Exception as db_err:
                    print(f"✗ Database error: {db_err}")
                    logger.error(f"Database error: {db_err}")
                finally:
                    if ctx:
                        ctx.pop()
            except Exception as db_error:
                print(f"✗ Database error: {db_error}")
                logger.error(f"Database error: {db_error}")
                # Continue processing even if logging fails
            
            # Handle based on policy decision
            if policy_decision.action == 'block':
                logger.warning(f"Email blocked: {policy_decision.reason}")
                return  # Don't forward
            elif policy_decision.action == 'quarantine':
                logger.info(f"Email quarantined: {policy_decision.reason}")
                # Still forward but log as quarantined
                message_to_send = policy_decision.original_message
            elif policy_decision.action == 'sanitize':
                logger.info(f"Email sanitized: {policy_decision.reason}")
                message_to_send = policy_decision.modified_message
            elif policy_decision.action == 'tag':
                logger.info(f"Email tagged: {policy_decision.reason}")
                message_to_send = policy_decision.modified_message
            else:
                message_to_send = message
            
            # Forward to upstream SMTP server (synchronous)
            if message_to_send:
                self._forward_message_sync(message_to_send)
            
        except Exception as e:
            logger.error(f"Error processing email: {e}", exc_info=True)
            # Log error
            try:
                from flask import has_app_context
                if has_app_context():
                    ctx = None
                else:
                    try:
                        import sys
                        import os
                        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        from app import app as flask_app
                        ctx = flask_app.app_context()
                        ctx.push()
                    except:
                        ctx = None
                
                try:
                    error_recipients = list(message.get_all('To', []))
                    
                    email_log = EmailLog(
                        message_id=message.get('Message-ID', 'unknown'),
                        sender=message.get('From', 'unknown'),
                        subject=message.get('Subject', ''),
                        status='error',
                        error_message=str(e),
                        processing_time_ms=(time.time() - start_time) * 1000
                    )
                    
                    # Add recipients (always as array)
                    for recipient in error_recipients:
                        recipient_obj = EmailRecipient(
                            email_address=recipient,
                            recipient_type='to'
                        )
                        email_log.recipients.append(recipient_obj)
                    
                    db.session.add(email_log)
                    db.session.commit()
                finally:
                    if ctx:
                        ctx.pop()
            except Exception as db_error:
                logger.error(f"Database error while logging error: {db_error}")
    
    def _extract_body_text(self, message: EmailMessage) -> str:
        """Extract plain text body from message."""
        body = ""
        
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        try:
                            body += payload.decode('utf-8', errors='ignore')
                        except:
                            pass
        else:
            payload = message.get_payload(decode=True)
            if payload:
                try:
                    body = payload.decode('utf-8', errors='ignore')
                except:
                    pass
        
        return body
    
    def _forward_message_sync(self, message: EmailMessage):
        """Forward message to upstream SMTP server (synchronous)."""
        try:
            self._send_smtp(message)
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
    
    def _send_smtp(self, message: EmailMessage):
        """Send message via SMTP (blocking)."""
        # Skip forwarding if upstream SMTP is not configured (for testing)
        if Config.UPSTREAM_SMTP_HOST == 'smtp.example.com':
            logger.info("Skipping forward - upstream SMTP not configured (OK for testing)")
            return
        
        try:
            # Remove Bcc header before forwarding (SMTP servers don't accept Bcc as a header)
            if 'Bcc' in message:
                del message['Bcc']
            
            # Extract sender
            sender = parseaddr(message.get('From', ''))[1]
            if not sender:
                sender = "no-reply@proxy"
            
            # Extract recipients (excluding Bcc since we removed the header)
            recipients = []
            for header in ['To', 'Cc']:
                addrs = message.get_all(header, [])
                for addr in addrs:
                    _, email_addr = parseaddr(addr)
                    if email_addr:
                        recipients.append(email_addr)
            
            if not recipients:
                logger.warning("No recipients found, skipping forward")
                return
            
            # Send using sendmail (explicitly sends MAIL FROM, RCPT TO, DATA)
            with smtplib.SMTP(Config.UPSTREAM_SMTP_HOST, Config.UPSTREAM_SMTP_PORT) as server:
                server.sendmail(sender, recipients, message.as_string())
                logger.info(f"Message forwarded to {len(recipients)} recipient(s)")
        except Exception as e:
            logger.warning(f"SMTP forward failed (this is OK for testing): {e}")
            # Don't raise - allow email to be logged even if forwarding fails

class SMTPProxy:
    """SMTP proxy server."""
    
    def __init__(self, app_context=None):
        """Initialize SMTP proxy.
        
        Args:
            app_context: Flask application context (optional, for database access)
        """
        self.detection_engine = DetectionEngine(enable_spacy=Config.ENABLE_SPACY)
        self.content_extractor = ContentExtractor(Config.TIKA_SERVER_URL)
        self.policy_engine = PolicyEngine(
            default_policy=Config.DEFAULT_POLICY,
            quarantine_dir=Config.QUARANTINE_DIR
        )
        self.controller = None
        self.app_context = app_context
        self.flask_app = None
    
    def start(self):
        """Start the SMTP proxy server."""
        handler = EmailHandler(
            self.detection_engine,
            self.content_extractor,
            self.policy_engine
        )
        
        self.controller = Controller(
            handler,
            hostname=Config.PROXY_HOST,
            port=Config.PROXY_PORT
        )
        
        # Check Tika availability
        if not self.content_extractor.is_tika_available():
            logger.warning("Tika server not available. Attachment extraction may fail.")
            logger.warning("Start Tika with: docker-compose up -d")
        
        logger.info(f"Starting SMTP proxy on {Config.PROXY_HOST}:{Config.PROXY_PORT}")
        logger.info(f"Forwarding to {Config.UPSTREAM_SMTP_HOST}:{Config.UPSTREAM_SMTP_PORT}")
        print(f"\n{'='*60}")
        print(f"✓ SMTP Proxy is listening on port {Config.PROXY_PORT}")
        print(f"✓ Ready to intercept emails...")
        print(f"✓ Handler type: {type(handler).__name__}")
        print(f"{'='*60}\n")
        
        self.controller.start()
        print(f"[DEBUG] Controller started: {self.controller}")
        print(f"[DEBUG] Controller running: {self.controller._thread.is_alive() if hasattr(self.controller, '_thread') else 'N/A'}\n")
    
    def stop(self):
        """Stop the SMTP proxy server."""
        if self.controller:
            self.controller.stop()
            logger.info("SMTP proxy stopped")


"""Email processor for handling intercepted emails."""
import logging
import time
import zipfile
import tarfile
from email.message import EmailMessage
from aiosmtpd.handlers import Message

from ...config import Config
from ...engines import DetectionEngine, ContentExtractor, PolicyEngine
from ..storage import AttachmentStorage
from ..database import EmailRepository
from ..smtp import SMTPForwarder
from ..websocket import WebSocketNotifier

logger = logging.getLogger(__name__)


class EmailProcessor(Message):
    """Processes intercepted emails through detection, policy, and logging."""
    
    def __init__(self, detection_engine: DetectionEngine, 
                 content_extractor: ContentExtractor,
                 policy_engine: PolicyEngine,
                 flask_app=None):
        super().__init__()
        self.detection_engine = detection_engine
        self.content_extractor = content_extractor
        self.policy_engine = policy_engine
        self.attachment_storage = AttachmentStorage()
        self.email_repository = EmailRepository(flask_app=flask_app)
        self.smtp_forwarder = SMTPForwarder()
        self.websocket_notifier = WebSocketNotifier()
    
    def handle_message(self, message: EmailMessage):
        """Process intercepted email (synchronous aiosmtpd handler)."""
        start_time = time.time()
        
        try:
            self._log_debug_info(message)
            metadata = self._extract_metadata(message)
            body_text = self._extract_body_text(message)
            attachment_texts, attachment_data, attachment_count = self._process_attachments(message)
            
            # Combine all text for detection
            all_text = body_text
            if attachment_texts:
                all_text += "\n\n" + "\n\n".join(attachment_texts)
            
            # Run detection
            detections = self.detection_engine.detect_patterns(
                all_text,
                min_confidence=Config.MIN_CONFIDENCE
            )
            
            self._print_detection_results(detections)
            
            # Apply policy
            policy_decision = self.policy_engine.evaluate(detections, message)
            self._print_policy_decision(policy_decision)
            
            # Save to database
            processing_time = (time.time() - start_time) * 1000
            email_log = self.email_repository.save(
                metadata, body_text, detections, policy_decision,
                attachment_data, attachment_count, processing_time
            )
            
            if email_log:
                print(f"✓ Email logged to database (ID: {email_log.id})")
                print(f"   View in dashboard: http://localhost:{Config.FLASK_PORT}")
                print(f"{'='*60}\n")
                self.websocket_notifier.notify_new_email(email_log)
            
            # Handle based on policy decision
            message_to_send = self._get_message_to_send(policy_decision, message)
            if message_to_send:
                self.smtp_forwarder.forward(message_to_send)
            
        except Exception as e:
            logger.error(f"Error processing email: {e}", exc_info=True)
            error_log = self.email_repository.save_error(message, e, start_time)
            if error_log:
                self.websocket_notifier.notify_new_email(error_log)
    
    def _log_debug_info(self, message: EmailMessage):
        """Log debug information about the message."""
        print(f"\n[DEBUG] handle_message called")
        print(f"[DEBUG] Message type: {type(message)}")
        print(f"[DEBUG] Message headers: {list(message.keys())}")
    
    def _extract_metadata(self, message: EmailMessage) -> dict:
        """Extract metadata from email message."""
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
        
        return {
            'message_id': message_id,
            'sender': sender,
            'recipients': recipients,
            'subject': subject
        }
    
    def _process_attachments(self, message: EmailMessage) -> tuple:
        """Process attachments and extract text content."""
        attachment_texts = []
        attachment_data = []
        attachment_count = 0
        
        if not message.is_multipart():
            return attachment_texts, attachment_data, attachment_count
        
        for part in message.walk():
            if part.get_content_disposition() == 'attachment':
                attachment_count += 1
                filename = part.get_filename()
                if not filename:
                    continue
                
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                
                # Save attachment
                file_path = self.attachment_storage.save(filename, payload)
                if file_path:
                    attachment_data.append((filename, file_path))
                    # Extract text from attachment
                    text = self._extract_attachment_text(file_path, filename)
                    if text:
                        attachment_texts.append(text)
        
        return attachment_texts, attachment_data, attachment_count
    
    def _extract_attachment_text(self, file_path: str, filename: str) -> str:
        """Extract text content from attachment."""
        try:
            # Check if it's an archive
            if zipfile.is_zipfile(file_path) or tarfile.is_tarfile(file_path):
                extracted = self.content_extractor.extract_from_archive(
                    file_path, 
                    max_depth=Config.MAX_ARCHIVE_DEPTH
                )
                return "\n\n".join(extracted.values())
            else:
                text = self.content_extractor.extract_text(
                    file_path,
                    max_size_mb=Config.MAX_ATTACHMENT_SIZE_MB
                )
                return text or ""
        except Exception as e:
            logger.error(f"Error processing attachment {filename}: {e}")
            return ""
    
    def _print_detection_results(self, detections):
        """Print detection results to console."""
        if detections:
            print(f"\n⚠️  SENSITIVE DATA DETECTED:")
            for det in detections:
                print(f"   - {det.pattern_type}: '{det.matched_text}' (confidence: {det.confidence:.2f})")
        else:
            print(f"\n✓ No sensitive data detected")
    
    def _print_policy_decision(self, policy_decision):
        """Print policy decision to console."""
        print(f"\n📋 Policy Decision: {policy_decision.action.upper()}")
        print(f"   Reason: {policy_decision.reason}")
    
    def _get_message_to_send(self, policy_decision, message: EmailMessage) -> EmailMessage:
        """Determine which message to send based on policy decision."""
        if policy_decision.action == 'block':
            logger.warning(f"Email blocked: {policy_decision.reason}")
            return None
        elif policy_decision.action == 'quarantine':
            logger.info(f"Email quarantined: {policy_decision.reason}")
            return policy_decision.original_message
        elif policy_decision.action == 'sanitize':
            logger.info(f"Email sanitized: {policy_decision.reason}")
            return policy_decision.modified_message
        elif policy_decision.action == 'tag':
            logger.info(f"Email tagged: {policy_decision.reason}")
            return policy_decision.modified_message
        else:
            return message
    
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


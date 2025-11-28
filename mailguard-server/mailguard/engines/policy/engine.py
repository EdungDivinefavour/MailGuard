"""Policy enforcement engine for email handling."""
import logging
import copy
from pathlib import Path
from typing import List, Dict
from email.message import EmailMessage
from dataclasses import asdict

from ...models import DetectionResult, PolicyDecision

logger = logging.getLogger(__name__)

class PolicyEngine:
    """Engine for enforcing data leakage prevention policies."""
    
    def __init__(self, default_policy: str = "tag", quarantine_dir: Path = None):
        """
        Initialize policy engine.
        
        Args:
            default_policy: Default action (block, sanitize, quarantine, tag)
            quarantine_dir: Directory for quarantined emails
        """
        self.default_policy = default_policy
        self.quarantine_dir = quarantine_dir or Path("./quarantine")
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
    
    def evaluate(self, detections: List[DetectionResult], 
                 message: EmailMessage) -> PolicyDecision:
        """
        Evaluate detections and determine policy action.
        
        Args:
            detections: List of detection results
            message: Original email message
            
        Returns:
            PolicyDecision object
        """
        if not detections:
            return PolicyDecision(
                action='allow',
                reason='No sensitive data detected',
                detections=[]
            )
        
        # Always use default policy since we have no specific rules
        action = self.default_policy
        
        detection_dicts = [asdict(d) for d in detections]
        
        if action == 'block':
            return self._block_message(message, detections, detection_dicts)
        elif action == 'quarantine':
            return self._quarantine_message(message, detections, detection_dicts)
        elif action == 'sanitize':
            return self._sanitize_message(message, detections, detection_dicts)
        elif action == 'tag':
            return self._tag_message(message, detections, detection_dicts)
        else:
            return PolicyDecision(
                action='allow',
                reason='No policy match',
                detections=detection_dicts
            )
    
    def _block_message(self, message: EmailMessage, detections: List[DetectionResult],
                      detection_dicts: List[Dict]) -> PolicyDecision:
        """Block the message from being sent."""
        reason = f"Blocked: {len(detections)} sensitive data pattern(s) detected"
        if detections:
            reason += f" (e.g., {detections[0].pattern_type})"
        
        return PolicyDecision(
            action='block',
            reason=reason,
            detections=detection_dicts,
            original_message=message
        )
    
    def _quarantine_message(self, message: EmailMessage, detections: List[DetectionResult],
                           detection_dicts: List[Dict]) -> PolicyDecision:
        """Quarantine the message."""
        from ...services.storage import QuarantineStorage
        
        quarantine_storage = QuarantineStorage(self.quarantine_dir)
        quarantine_path = quarantine_storage.save(message)
        
        if not quarantine_path:
            logger.error("Error quarantining message")
            # Fallback to blocking
            return self._block_message(message, detections, detection_dicts)
        
        reason = f"Quarantined: {len(detections)} sensitive data pattern(s) detected"
        if detections:
            reason += f" (e.g., {detections[0].pattern_type})"
        
        return PolicyDecision(
            action='quarantine',
            reason=reason,
            detections=detection_dicts,
            original_message=message,
            quarantine_path=quarantine_path
        )
    
    def _sanitize_message(self, message: EmailMessage, detections: List[DetectionResult],
                         detection_dicts: List[Dict]) -> PolicyDecision:
        """Sanitize sensitive data from message."""
        sanitized = copy.deepcopy(message)
        
        body = ""
        if sanitized.is_multipart():
            for part in sanitized.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = sanitized.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Replace detected patterns with [REDACTED]
        sanitized_body = body
        for detection in sorted(detections, key=lambda x: x.position[1], reverse=True):
            start, end = detection.position
            sanitized_body = sanitized_body[:start] + f"[REDACTED {detection.pattern_type.upper()}]" + sanitized_body[end:]
        
        if sanitized.is_multipart():
            for part in sanitized.walk():
                if part.get_content_type() == "text/plain":
                    part.set_payload(sanitized_body)
                    break
        else:
            sanitized.set_payload(sanitized_body)
        
        sanitized['X-Content-Sanitized'] = 'true'
        sanitized['X-Sanitization-Reason'] = f"{len(detections)} sensitive pattern(s) detected"
        
        reason = f"Sanitized: {len(detections)} sensitive data pattern(s) removed"
        if detections:
            reason += f" (e.g., {detection.pattern_type})"
        
        return PolicyDecision(
            action='sanitize',
            reason=reason,
            detections=detection_dicts,
            original_message=message,
            modified_message=sanitized
        )
    
    def _tag_message(self, message: EmailMessage, detections: List[DetectionResult],
                    detection_dicts: List[Dict]) -> PolicyDecision:
        """Tag message with warning headers."""
        tagged = copy.deepcopy(message)
        
        detection_types = list(set(d.pattern_type for d in detections))
        tagged['X-Sensitive-Data-Detected'] = 'true'
        tagged['X-Detection-Types'] = ', '.join(detection_types)
        tagged['X-Detection-Count'] = str(len(detections))
        
        original_subject = tagged.get('Subject', '')
        tagged['Subject'] = f"[SENSITIVE] {original_subject}"
        
        reason = f"Tagged: {len(detections)} sensitive data pattern(s) detected"
        if detections:
            reason += f" (e.g., {detection_types[0]})"
        
        return PolicyDecision(
            action='tag',
            reason=reason,
            detections=detection_dicts,
            original_message=message,
            modified_message=tagged
        )


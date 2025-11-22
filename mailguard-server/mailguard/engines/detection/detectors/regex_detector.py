"""Regex-based pattern detector."""
import re
import logging
from typing import List

from ....models import DetectionResult

logger = logging.getLogger(__name__)


class RegexDetector:
    """Handles regex-based pattern detection."""
    
    def __init__(self):
        """Initialize regex patterns."""
        self.patterns = {
            'credit_card': re.compile(
                r'\b(?:\d{4}[-\s]?){3}\d{4}\b'  # Format: XXXX-XXXX-XXXX-XXXX
            ),
            'sin': re.compile(
                r'\b\d{3}[-\s]?\d{3}[-\s]?\d{3}\b'  # Canadian SIN format
            ),
            'ssn': re.compile(
                r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'  # US SSN format
            ),
            'email': re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ),
        }
    
    def detect(self, text: str, min_confidence: float = 0.7) -> List[DetectionResult]:
        """Detect patterns using regex."""
        results = []
        for pattern_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                # Basic validation for credit cards
                if pattern_type == 'credit_card':
                    digits = re.sub(r'[^\d]', '', match.group())
                    if len(digits) != 16:  # Simple length check
                        continue
                
                confidence = self._calculate_confidence(pattern_type, match.group())
                if confidence >= min_confidence:
                    results.append(DetectionResult(
                        pattern_type=pattern_type,
                        matched_text=match.group(),
                        confidence=confidence,
                        position=(match.start(), match.end())
                    ))
        return results
    
    def _calculate_confidence(self, pattern_type: str, matched_text: str) -> float:
        """Calculate confidence score for a match."""
        confidence_scores = {
            'credit_card': 0.9,
            'sin': 0.85,
            'ssn': 0.85,
            'email': 0.6,
        }
        
        confidence = confidence_scores.get(pattern_type, 0.7)
        
        # Increase confidence if formatted with dashes/spaces
        if '-' in matched_text or ' ' in matched_text:
            confidence = min(confidence + 0.1, 1.0)
        
        return confidence


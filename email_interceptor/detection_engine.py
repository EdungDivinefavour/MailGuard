"""Detection engine for sensitive data patterns."""
import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DetectionResult:
    """Result of a detection pattern match."""
    pattern_type: str
    matched_text: str
    confidence: float
    position: Tuple[int, int]  # (start, end)

class DetectionEngine:
    """Engine for detecting sensitive data patterns."""
    
    def __init__(self, enable_spacy: bool = True):
        """Initialize detection engine."""
        self.enable_spacy = enable_spacy
        self.nlp = None
        
        if enable_spacy:
            try:
                import spacy
                # Try to load English model, fallback to basic if not available
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    logger.warning("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
                    self.enable_spacy = False
            except ImportError:
                logger.warning("spaCy not available. Install with: pip install spacy")
                self.enable_spacy = False
        
        # Compile regex patterns - core patterns only
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
    
    def detect_patterns(self, text: str, min_confidence: float = 0.7) -> List[DetectionResult]:
        """
        Detect sensitive patterns in text.
        
        Args:
            text: Text to analyze
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of DetectionResult objects
        """
        results = []
        
        # Regex-based detection
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
        
        # Optional spaCy-based NER detection (simplified)
        if self.enable_spacy and self.nlp and text:
            try:
                doc = self.nlp(text[:50000])  # Limit text size
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'ORG']:  # Only most relevant
                        confidence = 0.6
                        if confidence >= min_confidence:
                            results.append(DetectionResult(
                                pattern_type=f'ner_{ent.label_.lower()}',
                                matched_text=ent.text,
                                confidence=confidence,
                                position=(ent.start_char, ent.end_char)
                            ))
            except Exception as e:
                logger.warning(f"spaCy NER not available: {e}")
        
        # Remove duplicates (simple approach)
        seen = set()
        unique_results = []
        for result in results:
            key = (result.pattern_type, result.matched_text)
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return sorted(unique_results, key=lambda x: x.position[0])
    
    def _calculate_confidence(self, pattern_type: str, matched_text: str) -> float:
        """Calculate confidence score for a match."""
        # Simple confidence scores
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
    
    def summarize_detections(self, results: List[DetectionResult]) -> Dict[str, int]:
        """Summarize detection results by type."""
        summary = {}
        for result in results:
            summary[result.pattern_type] = summary.get(result.pattern_type, 0) + 1
        return summary


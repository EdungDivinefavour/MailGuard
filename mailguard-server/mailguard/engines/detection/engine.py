"""Detection engine for sensitive data patterns using Presidio."""
import logging
from typing import List, Dict

from ...models import DetectionResult
from .detectors import PresidioDetector, RegexDetector

logger = logging.getLogger(__name__)


class DetectionEngine:
    """Engine for detecting sensitive data patterns using Presidio."""
    
    def __init__(self, use_presidio: bool = True):
        """
        Initialize detection engine.
        
        Args:
            use_presidio: Use Presidio for detection (recommended)
        """
        self.use_presidio = use_presidio
        
        # Initialize detectors
        self.presidio_detector = None
        self.regex_detector = None
        
        if use_presidio:
            self.presidio_detector = PresidioDetector()
            if not self.presidio_detector.analyzer:
                logger.warning("Falling back to regex-based detection")
                self.presidio_detector = None
                self.regex_detector = RegexDetector()
        else:
            self.regex_detector = RegexDetector()
    
    def detect_patterns(self, text: str, min_confidence: float = 0.7) -> List[DetectionResult]:
        """
        Detect sensitive patterns in text using Presidio ML models.
        
        Args:
            text: Text to analyze
            min_confidence: Minimum confidence threshold (0.0-1.0)
            
        Returns:
            List of DetectionResult objects
        """
        if not text:
            return []
        
        results = []
        
        # Use Presidio for ML-based detection
        if self.presidio_detector:
            results = self.presidio_detector.detect(text, min_confidence)
            # Fallback to regex if Presidio fails or returns nothing
            if not results and self.regex_detector is None:
                self.regex_detector = RegexDetector()
        
        # Fallback to regex-based detection
        if not results and self.regex_detector:
            results = self.regex_detector.detect(text, min_confidence)
        
        # Remove duplicates
        return self._deduplicate_results(results)
    
    def _deduplicate_results(self, results: List[DetectionResult]) -> List[DetectionResult]:
        """Remove duplicate detection results."""
        seen = set()
        unique_results = []
        for result in results:
            key = (result.pattern_type, result.matched_text, result.position[0])
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return sorted(unique_results, key=lambda x: x.position[0])
    
    def summarize_detections(self, results: List[DetectionResult]) -> Dict[str, int]:
        """Summarize detection results by type."""
        summary = {}
        for result in results:
            summary[result.pattern_type] = summary.get(result.pattern_type, 0) + 1
        return summary

"""Presidio-based ML detector."""
import logging
from typing import List, Optional

from ....models import DetectionResult

logger = logging.getLogger(__name__)


class PresidioDetector:
    """Handles Presidio ML-based detection and initialization."""
    
    def __init__(self, analyzer: Optional[object] = None):
        """
        Initialize Presidio detector.
        
        Args:
            analyzer: Optional Presidio analyzer. If None, will attempt to create one.
        """
        if analyzer is None:
            analyzer = self.create_analyzer()
        self.analyzer = analyzer
    
    @staticmethod
    def create_analyzer() -> Optional[object]:
        """Create and configure Presidio analyzer."""
        try:
            from presidio_analyzer import AnalyzerEngine
            
            # Initialize Presidio with default configuration (uses built-in regex patterns)
            analyzer = AnalyzerEngine()
            
            # Add custom Canadian SIN pattern
            PresidioDetector._add_sin_recognizer(analyzer)
            
            logger.info("Presidio analyzer initialized with custom SIN pattern")
            return analyzer
                
        except ImportError:
            logger.warning("Presidio not available. Install with: pip install presidio-analyzer")
            return None
        except Exception as e:
            logger.error(f"Error initializing Presidio: {e}")
            return None
    
    @staticmethod
    def _add_sin_recognizer(analyzer):
        """Add Canadian SIN recognizer to analyzer."""
        try:
            from presidio_analyzer.pattern import Pattern
            from presidio_analyzer import PatternRecognizer
            
            sin_pattern = Pattern(
                name="canadian_sin",
                regex=r"\b\d{3}[-\s]?\d{3}[-\s]?\d{3}\b",
                score=0.85
            )
            sin_recognizer = PatternRecognizer(
                supported_entity="CANADIAN_SIN",
                patterns=[sin_pattern],
                context=["sin", "social insurance", "canadian sin"]
            )
            analyzer.registry.add_recognizer(sin_recognizer)
        except Exception:
            pass  # Fail silently if we can't add the recognizer
    
    def detect(self, text: str, min_confidence: float = 0.7) -> List[DetectionResult]:
        """Detect patterns using Presidio."""
        if not self.analyzer or not text:
            return []
        
        try:
            presidio_results = self.analyzer.analyze(
                text=text[:50000],  # Limit text size for performance
                language='en',
                entities=None,  # None means detect all supported entities
                score_threshold=min_confidence
            )
            
            # Map Presidio entity types to our format
            entity_type_mapping = {
                'CREDIT_CARD': 'credit_card',
                'SSN': 'ssn',
                'CANADIAN_SIN': 'sin',
                'EMAIL_ADDRESS': 'email',
                'PHONE_NUMBER': 'phone',
                'IBAN_CODE': 'iban',
                'IP_ADDRESS': 'ip_address',
                'PERSON': 'person',
                'ORGANIZATION': 'organization',
                'DATE_TIME': 'date_time',
                'LOCATION': 'location',
                'US_DRIVER_LICENSE': 'driver_license',
                'US_PASSPORT': 'passport',
                'US_BANK_NUMBER': 'bank_account',
            }
            
            results = []
            for result in presidio_results:
                pattern_type = entity_type_mapping.get(
                    result.entity_type, 
                    result.entity_type.lower()
                )
                
                matched_text = text[result.start:result.end]
                
                results.append(DetectionResult(
                    pattern_type=pattern_type,
                    matched_text=matched_text,
                    confidence=result.score,
                    position=(result.start, result.end)
                ))
            
            logger.debug(f"Presidio detected {len(results)} entities")
            return results
            
        except Exception as e:
            logger.error(f"Error in Presidio detection: {e}")
            return []

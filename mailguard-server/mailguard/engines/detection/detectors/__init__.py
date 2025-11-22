"""Detection detectors."""
from .presidio_detector import PresidioDetector
from .regex_detector import RegexDetector

__all__ = [
    'PresidioDetector',
    'RegexDetector'
]


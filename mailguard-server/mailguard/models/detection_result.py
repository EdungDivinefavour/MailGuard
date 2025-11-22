"""Detection result data class."""
from typing import Tuple
from dataclasses import dataclass

@dataclass
class DetectionResult:
    """Result of a detection pattern match."""
    pattern_type: str
    matched_text: str
    confidence: float
    position: Tuple[int, int]  # (start, end)


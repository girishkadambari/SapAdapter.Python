from typing import Any, List
from ..schemas.validation import ValidationResult
from ..schemas.extraction import BusinessExtraction

class ValidationEngine:
    """
    Calculates confidence and completeness for extractions.
    """
    
    def validate_extraction(self, extraction: BusinessExtraction) -> ValidationResult:
        """
        Validates a business extraction against expected rules.
        """
        errors = []
        warnings = []
        
        # Basic validation rule: check if any data was actually found
        if not extraction.data:
            errors.append("No data extracted for entity.")
            
        # Example: check for high-confidence markers
        confidence = extraction.confidence
        if not extraction.source_controls:
            confidence *= 0.5
            warnings.append("No source control lineage for extraction.")
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            confidence=confidence
        )

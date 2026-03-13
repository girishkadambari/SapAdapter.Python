from typing import List, Optional
from pydantic import BaseModel, Field

class ValidationResult(BaseModel):
    """
    Represents the result of a validation check on a screen or control.
    """
    is_valid: bool = Field(..., description="Whether the validation passed")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    confidence: float = Field(1.0, description="Overall confidence in the validation result")
    remediation: Optional[str] = Field(None, description="Suggested action to fix validation issues")

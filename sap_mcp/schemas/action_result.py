from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .observation import ScreenObservation

class ActionResult(BaseModel):
    """
    Standardized result for a SAP action.
    """
    success: bool = Field(..., description="Whether the action was successful")
    action_type: str = Field(..., description="The action that was performed")
    target_id: Optional[str] = Field(None, description="The target of the action")
    observation: Optional[ScreenObservation] = Field(None, description="The observation captured after the action")
    error: Optional[str] = Field(None, description="Error message if success is False")
    message: Optional[str] = Field(None, description="Informational message about the result")
    confidence: float = Field(1.0, description="Confidence score for the action outcome")

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from .observation import ScreenObservation

class ActionResult(BaseModel):
    """
    Standardized result for a SAP action enriched for AI agents.
    """
    success: bool = Field(..., description="Whether the action was successful")
    action_type: str = Field(..., description="The action that was performed")
    target_id: Optional[str] = Field(None, description="The target of the action if applicable")
    observation: Optional[ScreenObservation] = Field(None, description="The observation captured after the action")
    
    # Enriched diagnostic fields for AI
    error: Optional[str] = Field(None, description="Detailed error message if success is False")
    message: Optional[str] = Field(None, description="Informational message about the result")
    warnings: List[str] = Field(default_factory=list, description="Warnings or non-fatal issues (e.g. from SAP status bar)")
    
    # Action impact details
    is_modal_active: bool = Field(False, description="Whether a modal dialog is currently blocking the screen")
    verification_outcome: str = Field("SUCCESS", description="Outcome of the verification strategy (SUCCESS, TIMEOUT, UNVERIFIED)")
    what_changed: Optional[str] = Field(None, description="Summary of significant state changes detected after the action")
    completed_action_details: Dict[str, Any] = Field(default_factory=dict, description="Specific details of what was mutated (e.g., old value -> new value)")
    
    confidence: float = Field(1.0, description="Confidence score for the action outcome")

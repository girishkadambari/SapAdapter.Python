from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .observation import ScreenObservation

class ActionResult(BaseModel):
    """
    Standardized result for a SAP action.
    """
    ok: bool = Field(..., description="Whether the action was successful")
    action: str = Field(..., description="The action that was performed")
    target: Optional[str] = Field(None, description="The target of the action")
    effects: Dict = Field(default_factory=dict, description="Changes observed as a result of the action")
    new_observation: Optional[ScreenObservation] = Field(None, description="The observation captured after the action")
    warnings: List[str] = Field(default_factory=list, description="Any warnings encountered during execution")
    error: Optional[str] = Field(None, description="Error message if ok is False")
    confidence: float = Field(1.0, description="Confidence score for the action outcome")

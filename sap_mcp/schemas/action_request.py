from typing import Dict, Optional
from pydantic import BaseModel, Field

class ActionRequest(BaseModel):
    """
    Standardized request for a SAP action.
    """
    action_type: str = Field(..., description="Type of action (e.g., set_field, press_button, navigate_tcode)")
    target: Dict = Field(default_factory=dict, description="Metadata identifying the target control or location")
    params: Dict = Field(default_factory=dict, description="Input parameters for the action")
    session_id: str = Field(..., description="The session the action should be performed in")
    expected_state: Optional[Dict] = Field(None, description="Optional criteria to verify the success of the action")

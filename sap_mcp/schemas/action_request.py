from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

class ActionRequest(BaseModel):
    """
    Standardized request for a SAP action.
    """
    action_type: str = Field(..., description="Type of action (e.g., set_field, press_button, navigate_tcode)")
    target_id: Optional[str] = Field(None, description="The SAP GUI ID of the target control. Can be None for global actions like send_vkey.")
    params: Dict[str, Any] = Field(default_factory=dict, description="Input parameters for the action")
    session_id: str = Field(..., description="The session the action should be performed in")
    expected_state: Optional[Dict[str, Any]] = Field(None, description="Optional criteria to verify the success of the action")
    verification_mode: str = Field("wait_idle", description="Strategy to verify action completion (e.g. 'wait_idle', 'wait_screen_change')")

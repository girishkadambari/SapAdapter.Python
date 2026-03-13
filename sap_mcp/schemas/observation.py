from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .control import Control

class StatusBar(BaseModel):
    """
    Represents the state of the SAP Status Bar.
    """
    type: str = Field(..., description="Message type: S (Success), W (Warning), E (Error), A (Abend), I (Info)")
    text: str = Field(..., description="The message text")
    msg_id: Optional[str] = Field(None, description="SAP Message ID")
    msg_no: Optional[str] = Field(None, description="SAP Message Number")

class Modal(BaseModel):
    """
    Represents an active modal dialog.
    """
    id: str = Field(..., description="SAP GUI ID of the modal window")
    title: str = Field(..., description="Title of the modal window")
    text: Optional[str] = Field(None, description="Content text of the modal if available")

class ValidationSummary(BaseModel):
    """
    Summary of screen validation status.
    """
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class ScreenObservation(BaseModel):
    """
    Represents a structured snapshot of the current SAP screen.
    """
    session_id: str = Field(..., description="The ID of the SAP session")
    transaction: str = Field(..., description="The current Transaction Code (T-Code)")
    title: str = Field(..., description="The window title")
    program: Optional[str] = Field(None, description="The ABAP program name")
    status_bar: StatusBar = Field(..., description="The current status bar state")
    modal: Optional[Modal] = Field(None, description="Details of any active modal dialog")
    controls: List[Control] = Field(default_factory=list, description="List of all visible controls")
    screen_type: str = Field("UNKNOWN", description="The classified type of the screen (e.g. SEARCH_INPUT, DETAIL_VIEW)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")
    screenshot_ref: Optional[str] = Field(None, description="Reference to a captured screenshot file")
    screenshot_data: Optional[str] = Field(None, description="Base64 encoded screenshot image data")
    validation_summary: ValidationSummary = Field(default_factory=ValidationSummary)

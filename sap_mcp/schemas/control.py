from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

class Control(BaseModel):
    """
    Represents a single SAP GUI component.
    """
    id: str = Field(..., description="The unique SAP GUI ID of the control (e.g., wnd[0]/usr/txtVBAK-VBELN)")
    type: str = Field(..., description="The SAP GUI scripting type (e.g., GuiTextField)")
    subtype: Optional[str] = Field(None, description="Detailed subtype if applicable")
    label: Optional[str] = Field(None, description="Human-readable label or tooltip associated with the control")
    value: Optional[str] = Field(None, description="The current value or text of the control")
    editable: bool = Field(True, description="Whether the control can be modified")
    enabled: bool = Field(True, description="Whether the control is currently active")
    visible: bool = Field(True, description="Whether the control is visible on the screen")
    required: bool = Field(False, description="Whether the control is a required field")
    parent_id: Optional[str] = Field(None, description="The ID of the parent container")
    bounds: Optional[Tuple[int, int, int, int]] = Field(None, description="Screen coordinates (x, y, width, height)")
    actions: List[str] = Field(default_factory=list, description="Supported actions for this control")
    confidence: float = Field(1.0, description="Confidence score for the extraction of this control")

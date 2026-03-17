from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field

class ActionDefinition(BaseModel):
    """
    Defines how to execute an action on a control via an MCP tool.
    """
    name: str = Field(..., description="Logical name of the action (e.g. 'set_value', 'select_row')")
    tool: str = Field(..., description="The MCP tool name to use (e.g. 'sap_interact_field')")
    action_type: str = Field(..., description="The value to pass for the 'action_type' parameter")
    description: str = Field(..., description="Human-readable description of what this action does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Pre-filled or guided parameters for the tool call")

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
    children: List[Any] = Field(default_factory=list, description="Child controls if this is a container")
    actions: List[str] = Field(default_factory=list, description="Legacy list of action names")
    supported_methods: List[ActionDefinition] = Field(default_factory=list, description="Structured mapping of actions to MCP tools")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")
    confidence: float = Field(1.0, description="Confidence score for the extraction of this control")

from typing import Any, List, Optional
from .base_handler import BaseControlHandler
from ..schemas.control import Control

class ShellHandler(BaseControlHandler):
    """
    Handler for GuiShell. This is a generic container for ALV Grids, Trees, etc.
    It identifies the specific child control and delegates where possible.
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == "GuiShell"

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        subtype = str(getattr(control, "SubType", "shell")).lower()
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype=subtype,
            label=props["tooltip"] or f"SAP {subtype}",
            value=f"Shell Control: {subtype}",
            editable=False,
            visible=props["visible"],
            parent_id=props["parent_id"],
            actions=self.get_supported_actions(control),
            confidence=1.0
        )

    def get_supported_actions(self, control: Any) -> List[str]:
        subtype = str(getattr(control, "SubType", "")).lower()
        if "grid" in subtype:
            return ["get_rows", "find_row", "double_click"]
        if "tree" in subtype:
            return ["expand_node", "select_node"]
        return ["focus"]

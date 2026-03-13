from typing import Any, List, Dict
from .base_handler import BaseControlHandler
from ..schemas.control import Control

class TreeHandler(BaseControlHandler):
    """
    Handler for GuiTree.
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == "GuiTree"

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype="tree",
            label=props["tooltip"] or "SAP Tree",
            value="Tree Control",
            editable=False,
            visible=props["visible"],
            parent_id=props["parent_id"],
            actions=self.get_supported_actions(control),
            confidence=1.0
        )

    def get_supported_actions(self, control: Any) -> List[str]:
        return ["expand_node", "collapse_node", "select_node", "get_nodes"]

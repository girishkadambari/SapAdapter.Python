from typing import Any, List
from .base_handler import BaseControlHandler
from ..schemas.control import Control

class TabHandler(BaseControlHandler):
    """
    Handler for tabs and tab strips.
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == "GuiTab"

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype="tab",
            label=props["text"],
            value="active" if getattr(control, "Selected", False) else "inactive",
            editable=False,
            visible=props["visible"],
            parent_id=props["parent_id"],
            actions=self.get_supported_actions(control),
            confidence=1.0
        )

    def get_supported_actions(self, control: Any) -> List[str]:
        actions = ["select"]
        return actions

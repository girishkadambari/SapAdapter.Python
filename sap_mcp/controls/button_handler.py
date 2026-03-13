from typing import Any, List
from .base_handler import BaseControlHandler
from ..schemas.control import Control

class ButtonHandler(BaseControlHandler):
    """
    Handler for buttons and toolbar elements.
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == "GuiButton"

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype="button",
            label=props["text"] or props["tooltip"],
            value=None,
            editable=False,
            enabled=bool(getattr(control, "Enabled", True)),
            visible=props["visible"],
            parent_id=props["parent_id"],
            actions=self.get_supported_actions(control),
            confidence=1.0
        )

    def get_supported_actions(self, control: Any) -> List[str]:
        actions = []
        if bool(getattr(control, "Enabled", True)):
            actions.append("press")
        return actions

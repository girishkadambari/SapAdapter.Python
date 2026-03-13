from typing import Any, List
from .base_handler import BaseControlHandler
from ..schemas.control import Control

class ModalHandler(BaseControlHandler):
    """
    Handler for modal windows.
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == "GuiModalWindow"

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype="modal",
            label=props["text"],
            value=None,
            editable=False,
            visible=True,
            parent_id=None,
            actions=self.get_supported_actions(control),
            confidence=1.0
        )

    def get_supported_actions(self, control: Any) -> List[str]:
        return ["close", "focus"]

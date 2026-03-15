from typing import Any
from .base_extractor import BaseControlExtractor
from ...schemas.control import Control
from ...core.config import SapGuiTypes, ControlSubtypes

class ButtonExtractor(BaseControlExtractor):
    """
    Extractor for buttons and toolbar elements.
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == SapGuiTypes.BUTTON

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype=ControlSubtypes.BUTTON,
            text=props["text"],
            value=props["text"],
            visible=props["visible"],
            editable=props["changeable"],
            bounds=props.get("bounds")
        )

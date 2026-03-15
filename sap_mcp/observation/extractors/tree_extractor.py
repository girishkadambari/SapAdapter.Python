from typing import Any
from .base_extractor import BaseControlExtractor
from ...schemas.control import Control
from ...core.config import SapGuiTypes, ControlSubtypes

class TreeExtractor(BaseControlExtractor):
    """
    Extractor for GuiTree.
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == SapGuiTypes.TREE

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype=ControlSubtypes.TREE,
            text=props["text"],
            visible=props["visible"],
            editable=props["changeable"],
            bounds=props.get("bounds"),
            parent_id=props["parent_id"],
            confidence=1.0
        )

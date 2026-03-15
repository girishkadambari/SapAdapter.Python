from typing import Any
from .base_extractor import BaseControlExtractor
from ...schemas.control import Control
from ...core.config import SapGuiTypes, ControlSubtypes

class FieldExtractor(BaseControlExtractor):
    """
    Extractor for input fields, checkboxes, and radio buttons.
    """
    
    def identify(self, control: Any) -> bool:
        sap_type = str(control.Type)
        return sap_type in [
            SapGuiTypes.TEXT_FIELD, 
            SapGuiTypes.C_TEXT_FIELD, 
            SapGuiTypes.CHECKBOX, 
            SapGuiTypes.RADIO_BUTTON, 
            SapGuiTypes.PASSWORD_FIELD
        ]

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        sap_type = props["type"]
        
        kind = ControlSubtypes.TEXT
        if sap_type == SapGuiTypes.CHECKBOX: kind = ControlSubtypes.CHECKBOX
        elif sap_type == SapGuiTypes.RADIO_BUTTON: kind = ControlSubtypes.RADIO
        elif sap_type == SapGuiTypes.PASSWORD_FIELD: kind = ControlSubtypes.PASSWORD
        
        value = props["text"]
        if kind in (ControlSubtypes.CHECKBOX, ControlSubtypes.RADIO):
            value = str(getattr(control, "Selected", False))
        elif kind == ControlSubtypes.COMBOBOX or sap_type == SapGuiTypes.COMBOBOX:
            kind = ControlSubtypes.COMBOBOX
            value = str(getattr(control, "Key", ""))

        return Control(
            id=props["id"],
            type=sap_type,
            subtype=kind,
            label=props["tooltip"],
            value=value,
            editable=props["changeable"],
            visible=props["visible"],
            parent_id=props["parent_id"],
            confidence=1.0
        )

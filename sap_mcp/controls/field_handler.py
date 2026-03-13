from typing import Any, List
from .base_handler import BaseControlHandler
from ..schemas.control import Control

class FieldHandler(BaseControlHandler):
    """
    Handler for input fields, checkboxes, and radio buttons.
    """
    
    def identify(self, control: Any) -> bool:
        sap_type = str(control.Type)
        return sap_type in ["GuiTextField", "GuiCTextField", "GuiCheckBox", "GuiRadioButton", "GuiPasswordField"]

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        sap_type = props["type"]
        
        kind = "text"
        if sap_type == "GuiCheckBox": kind = "checkbox"
        elif sap_type == "GuiRadioButton": kind = "radio"
        elif sap_type == "GuiPasswordField": kind = "password"
        
        value = props["text"]
        if kind == "checkbox" or kind == "radio":
            value = "selected" if getattr(control, "Selected", False) else "unselected"

        return Control(
            id=props["id"],
            type=sap_type,
            subtype=kind,
            label=props["tooltip"],
            value=value,
            editable=props["changeable"],
            visible=props["visible"],
            parent_id=props["parent_id"],
            actions=self.get_supported_actions(control),
            confidence=1.0
        )

    def get_supported_actions(self, control: Any) -> List[str]:
        actions = []
        if bool(getattr(control, "Changeable", False)):
            sap_type = str(control.Type)
            if sap_type in ["GuiTextField", "GuiCTextField", "GuiPasswordField"]:
                actions.append("set_text")
            elif sap_type in ["GuiCheckBox", "GuiRadioButton"]:
                actions.append("select")
        return actions

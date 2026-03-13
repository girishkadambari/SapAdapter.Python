from typing import Any, Dict, List
from ..schemas.control import Control
from ..schemas.observation import ScreenObservation, StatusBar, Modal

class NormalizedSnapshotBuilder:
    """
    Converts raw SAP data into canonical ScreenObservation and Control models.
    """
    
    # Mapping of SAP GuiComponent Types to our internal kinds
    TYPE_MAP = {
        "GuiTextField": "text",
        "GuiCTextField": "text",
        "GuiPasswordField": "password",
        "GuiLabel": "label",
        "GuiButton": "button",
        "GuiCheckBox": "checkbox",
        "GuiRadioButton": "radio",
        "GuiComboBox": "combobox",
        "GuiTab": "tab",
        "GuiMenu": "menu",
        "GuiToolbar": "toolbar",
        "GuiStatusbar": "statusbar",
        "GuiTableControl": "table",
        "GuiGridView": "grid",
        "GuiTree": "tree",
        "GuiShell": "shell",
    }

    def normalize_control(self, raw: Dict[str, Any]) -> Control:
        """
        Maps raw properties to a structured Control model.
        """
        sap_type = raw.get("type", "unknown")
        kind = self.TYPE_MAP.get(sap_type, "unknown")
        
        # Clean ID (remove session prefix)
        raw_id = raw.get("id", "")
        clean_id = raw_id
        if "/wnd[" in raw_id:
            clean_id = "wnd[" + raw_id.split("/wnd[")[-1]

        return Control(
            id=clean_id,
            type=sap_type,
            subtype=kind,
            label=raw.get("tooltip") or raw.get("text") if kind == "label" else raw.get("tooltip"),
            value=raw.get("text") if kind != "label" else None,
            editable=raw.get("changeable", False),
            visible=raw.get("visible", True),
            parent_id=raw.get("parent_id"),
            bounds=raw.get("bounds"),
            actions=self._infer_actions(kind, raw.get("changeable", False)),
            confidence=1.0
        )

    def _infer_actions(self, kind: str, editable: bool) -> List[str]:
        """
        Infers supported actions based on control kind.
        """
        actions = []
        if kind == "button": actions.append("press")
        if kind == "text" and editable: 
            actions.append("set_value")
            actions.append("get_value")
        if kind == "checkbox": actions.append("toggle")
        if kind == "tab": actions.append("select")
        return actions

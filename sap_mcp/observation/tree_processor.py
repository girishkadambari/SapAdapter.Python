from typing import Any, Dict, List, Optional
from ..schemas.control import Control
from ..core.config import SapGuiTypes, ControlSubtypes

class TreeProcessor:
    """
    Handles the mapping of raw SAP GUI tree data (from GetObjectTree) 
    into structured Control models.
    """

    def process_json_tree(self, tree: Dict[str, Any]) -> List[Control]:
        """
        Processes the optimized JSON tree into a flat list of Control models.
        """
        controls = []
        
        def flatten(node):
            props = node.get("properties", {})
            if props:
                control = self.map_node_to_control(props)
                if control:
                    controls.append(control)
            
            for child in node.get("children", []):
                flatten(child)
        
        flatten(tree)
        return controls

    def map_node_to_control(self, props: Dict[str, Any]) -> Optional[Control]:
        """
        Maps a properties dictionary from GetObjectTree to a Control model.
        """
        sap_id = props.get("Id")
        sap_type = props.get("Type")
        
        if not sap_id or not sap_type:
            return None

        subtype = self._determine_subtype(sap_id, sap_type)
        
        # Normalize ID
        norm_id = sap_id
        if "/wnd[" in sap_id:
            norm_id = "wnd[" + sap_id.split("/wnd[")[-1]

        # Parse bounds
        bounds = self._parse_bounds(props)

        return Control(
            id=norm_id,
            type=sap_type,
            subtype=subtype,
            label=props.get("Tooltip") or props.get("Text") or "",
            value=props.get("Text") or "",
            editable=self._to_bool(props.get("Changeable"), False),
            enabled=self._to_bool(props.get("Visible"), True),
            visible=self._to_bool(props.get("Visible"), True),
            required=False,
            parent_id=None,
            bounds=bounds,
            confidence=1.0
        )

    def _determine_subtype(self, sap_id: str, sap_type: str) -> str:
        if sap_type in (SapGuiTypes.BUTTON, "GuiButton"): return ControlSubtypes.BUTTON
        if sap_type in (SapGuiTypes.TEXT_FIELD, SapGuiTypes.C_TEXT_FIELD, "GuiTextField", "GuiCTextField"): return ControlSubtypes.TEXT
        if sap_type in (SapGuiTypes.CHECKBOX, "GuiCheckBox"): return ControlSubtypes.CHECKBOX
        if sap_type in (SapGuiTypes.RADIO_BUTTON, "GuiRadioButton"): return ControlSubtypes.RADIO
        if sap_type in (SapGuiTypes.COMBOBOX, "GuiComboBox"): return ControlSubtypes.COMBOBOX
        if sap_type in (SapGuiTypes.TAB, "GuiTab"): return ControlSubtypes.TAB
        if sap_id.endswith("StatusBar"): return "statusbar"
        if sap_type in ("GuiShell"): return "shell"
        if sap_type == "GuiLabel": return "label"
        if sap_type == "GuiStatusbar": return "statusbar"
        if sap_type == "GuiToolbar": return "toolbar"
        return "unknown"

    def _parse_bounds(self, props: Dict[str, Any]) -> Optional[tuple]:
        if all(k in props for k in ["Left", "Top", "Width", "Height"]):
            l, t, w, h = props["Left"], props["Top"], props["Width"], props["Height"]
            if l != "" and t != "":
                try:
                    return (int(l.strip()), int(t.strip()), int(w.strip()), int(h.strip()))
                except: pass
        return None

    def _to_bool(self, val: Any, default: bool = False) -> bool:
        if isinstance(val, bool): return val
        if isinstance(val, str):
            v = val.lower().strip()
            if v in ("true", "x", "1"): return True
            if v in ("false", "0"): return False
            if v == "": return default
        return default

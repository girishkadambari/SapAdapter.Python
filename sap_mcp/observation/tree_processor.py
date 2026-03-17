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
        Processes the optimized JSON tree into a hierarchical list of Control models.
        """
        # GetObjectTree usually returns a single root node dictionary.
        # We start recursion from there.
        root_controls = self._map_recursive(tree)
        return root_controls

    def _map_recursive(self, node: Dict[str, Any], parent_id: Optional[str] = None) -> List[Control]:
        """
        Recursively processes a node and its children.
        """
        controls = []
        props = node.get("properties", {})
        
        # Determine current node's control model
        control = None
        current_id = parent_id
        if props:
            control = self.map_node_to_control(props)
            if control:
                control.parent_id = parent_id
                current_id = control.id
                controls.append(control)
        
        # Recursively process children
        children_nodes = node.get("children", [])
        child_controls = []
        for child_node in children_nodes:
            child_controls.extend(self._map_recursive(child_node, current_id))
            
        # Attach children to the parent control if it exists
        if control:
            control.children = child_controls
        else:
            # If the current node didn't map to a control but has children,
            # elevate the children to the current level.
            controls.extend(child_controls)
            
        return controls

    def map_node_to_control(self, props: Dict[str, Any]) -> Optional[Control]:
        """
        Maps a properties dictionary from GetObjectTree to a Control model.
        """
        sap_id = props.get("Id")
        sap_type = props.get("Type")
        
        if not sap_id or not sap_type:
            return None

        subtype = self._determine_subtype(sap_id, sap_type, props)
        
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

    def _determine_subtype(self, sap_id: str, sap_type: str, props: Dict[str, Any] = {}) -> str:
        if sap_type in (SapGuiTypes.BUTTON, "GuiButton"): return ControlSubtypes.BUTTON
        if sap_type in (SapGuiTypes.TEXT_FIELD, SapGuiTypes.C_TEXT_FIELD, "GuiTextField", "GuiCTextField"): return ControlSubtypes.TEXT
        if sap_type in (SapGuiTypes.CHECKBOX, "GuiCheckBox"): return ControlSubtypes.CHECKBOX
        if sap_type in (SapGuiTypes.RADIO_BUTTON, "GuiRadioButton"): return ControlSubtypes.RADIO
        if sap_type in (SapGuiTypes.COMBOBOX, "GuiComboBox"): return ControlSubtypes.COMBOBOX
        if sap_type in (SapGuiTypes.TAB, "GuiTab"): return ControlSubtypes.TAB
        if sap_id.endswith("StatusBar"): return "statusbar"
        if sap_type in ("GuiShell"):
            shell_subtype = props.get("SubType", "")
            label = (props.get("Text") or props.get("Tooltip") or "").lower()
            if "GridView" in shell_subtype or "gridview" in label or "grid" in label: return ControlSubtypes.GRID
            if "Tree" in shell_subtype or "tree" in label: return ControlSubtypes.TREE
            return "shell"
        if sap_type in (SapGuiTypes.LABEL, "GuiLabel"): return ControlSubtypes.LABEL
        if sap_type in (SapGuiTypes.STATUSBAR, "GuiStatusbar"): return ControlSubtypes.STATUSBAR
        if sap_type in (SapGuiTypes.TOOLBAR, "GuiToolbar"): return "toolbar"
        if sap_type in (SapGuiTypes.MENU, "GuiMenu"): return ControlSubtypes.MENU
        
        return ControlSubtypes.UNKNOWN

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

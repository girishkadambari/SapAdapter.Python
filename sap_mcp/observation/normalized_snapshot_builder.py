from typing import Dict, Any, List
from ..schemas.control import Control, ActionDefinition

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
        sap_type = raw.get("type") or raw.get("Type", "unknown")
        kind = self.TYPE_MAP.get(sap_type, "unknown")
        
        # Mapping for optimized tree property names (Id vs id)
        raw_id = raw.get("id") or raw.get("Id", "")
        clean_id = raw_id
        if "/wnd[" in raw_id:
            clean_id = "wnd[" + raw_id.split("/wnd[")[-1]

        # Use GetObjectTree property names if present
        text = raw.get("text") or raw.get("Text", "")
        tooltip = raw.get("tooltip") or raw.get("Tooltip", "")
        changeable = raw.get("changeable", raw.get("Changeable", False))
        visible = raw.get("visible", raw.get("Visible", True))

        methods = self._define_methods(kind, changeable, raw)
        
        return Control(
            id=clean_id,
            type=sap_type,
            subtype=kind,
            label=tooltip or text if kind == "label" else tooltip,
            value=text if kind != "label" else None,
            editable=changeable,
            visible=visible,
            parent_id=raw.get("parent_id"),
            bounds=raw.get("bounds"),
            actions=[m.name for m in methods],
            supported_methods=methods,
            metadata=self._extract_metadata(kind, raw),
            confidence=1.0
        )

    def normalize_optimized_tree(self, optimized_data: List[Dict[str, Any]]) -> List[Control]:
        """Processes a list of controls returned by GetObjectTree."""
        return [self.normalize_control(raw) for raw in optimized_data]

    def _extract_metadata(self, kind: str, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts specialized metadata for compound components."""
        meta = {}
        if kind == "table":
            meta.update(raw.get("table_metadata", {}))
        elif kind in ("grid", "shell"):
            meta.update(raw.get("grid_metadata", {}))
            if "shell_subtype" in raw:
                meta["subtype"] = raw["shell_subtype"]
        elif kind == "tree":
            meta.update(raw.get("tree_metadata", {}))
        return meta

    def _define_methods(self, kind: str, editable: bool, raw: Dict[str, Any]) -> List[ActionDefinition]:
        """
        Defines precise tool mappings for each control type.
        """
        methods = []
        
        if kind == "button":
            methods.append(ActionDefinition(
                name="press", tool="sap_interact_field", action_type="press_button",
                description="Click the button."
            ))

        if kind == "text" and editable:
            methods.append(ActionDefinition(
                name="set_value", tool="sap_interact_field", action_type="set_field",
                description="Enter text into the field."
            ))

        if kind == "checkbox":
            methods.append(ActionDefinition(
                name="toggle", tool="sap_interact_field", action_type="set_checkbox",
                description="Check or uncheck the box."
            ))

        if kind == "combobox":
            methods.append(ActionDefinition(
                name="select", tool="sap_interact_field", action_type="set_field",
                description="Select a value from the dropdown by key."
            ))

        if kind == "tab":
            methods.append(ActionDefinition(
                name="select", tool="sap_interact_field", action_type="select_tab",
                description="Switch to this tab."
            ))

        # Compound Component Methods
        if kind in ("table", "grid"):
            methods.extend([
                ActionDefinition(name="set_cell", tool="sap_table_action", action_type="set_cell_data", description="Set value at (row, column)."),
                ActionDefinition(name="get_cell", tool="sap_table_action", action_type="get_cell_data", description="Read value from (row, column)."),
                ActionDefinition(name="activate_cell", tool="sap_table_action", action_type="activate_cell", description="Double-click a cell."),
                ActionDefinition(name="search", tool="sap_table_action", action_type="find_row_by_text", description="Search for row with specific text.")
            ])

        if kind == "tree":
            methods.extend([
                ActionDefinition(name="select_node", tool="sap_tree_action", action_type="select_node", description="Select a tree node by key."),
                ActionDefinition(name="expand", tool="sap_tree_action", action_type="expand_node", description="Expand a folder node.")
            ])

        if kind == "shell":
            subtype = raw.get("shell_subtype", "")
            if subtype == "Toolbar":
                methods.append(ActionDefinition(
                    name="press_button", tool="sap_shell_action", action_type="press_button",
                    description="Click a toolbar button by ID or tooltip."
                ))
            elif subtype == "GridView":
                methods.extend([
                    ActionDefinition(name="set_cell", tool="sap_table_action", action_type="set_cell_data", description="Modify ALV cell."),
                    ActionDefinition(name="select_row", tool="sap_table_action", action_type="select_row", description="Select an ALV row.")
                ])

        return methods

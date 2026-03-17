from typing import List, Dict, Any
from ..schemas.control import Control, ActionDefinition
from ..core.config import ActionTypes, ControlSubtypes

class ControlEnricher:
    """
    Service to add semantic hints and action mappings to extracted controls.
    """
    
    def enrich(self, control: Control) -> Control:
        """
        Main entry point for enrichment logic.
        """
        control.supported_methods = self._define_methods(control.subtype, control.editable)
        
        # Link tools to the methods for agentic guidance
        control.actions = [m.tool for m in control.supported_methods]
        
        return control

    def _define_methods(self, subtype: str, editable: bool) -> List[ActionDefinition]:
        """
        Maps subtypes to allowed interaction methods.
        """
        methods = []
        
        if subtype == ControlSubtypes.BUTTON:
            methods.append(ActionDefinition(
                name="press",
                tool="sap_shell_action",
                action_type=ActionTypes.PRESS_BUTTON,
                description="Clicks the button"
            ))
            
        elif subtype == ControlSubtypes.TEXT:
            if editable:
                methods.append(ActionDefinition(
                    name="set_text",
                    tool="sap_interact_field",
                    action_type=ActionTypes.SET_FIELD,
                    description="Sets the text value"
                ))
                
        elif subtype == ControlSubtypes.CHECKBOX:
            methods.append(ActionDefinition(
                name="set_state",
                tool="sap_interact_field",
                action_type=ActionTypes.SET_CHECKBOX,
                description="Checks/Unchecks the box"
            ))
            
        elif subtype == ControlSubtypes.RADIO:
            methods.append(ActionDefinition(
                name="select",
                tool="sap_interact_field",
                action_type=ActionTypes.SELECT_RADIO,
                description="Selects the radio option"
            ))
            
        elif subtype == ControlSubtypes.COMBOBOX:
            methods.append(ActionDefinition(
                name="select_item",
                tool="sap_interact_field",
                action_type=ActionTypes.SET_FIELD,
                description="Selects an item by Key"
            ))
            
        elif subtype == ControlSubtypes.TABLE:
            methods.append(ActionDefinition(
                name="set_cell",
                tool="sap_table_action",
                action_type=ActionTypes.SET_CELL_DATA,
                description="Writes to a specific cell"
            ))
            methods.append(ActionDefinition(
                name="batch_fill",
                tool="sap_table_action",
                action_type=ActionTypes.TABLE_BATCH_FILL,
                description="Fills multiple rows efficiently"
            ))
            
        elif subtype == ControlSubtypes.GRID:
            methods.append(ActionDefinition(
                name="get_cell",
                tool="sap_table_action",
                action_type=ActionTypes.GET_CELL_DATA,
                description="Reads data from a cell"
            ))
            methods.append(ActionDefinition(
                name="select_row",
                tool="sap_table_action",
                action_type=ActionTypes.SELECT_ROW,
                description="Selects a logical row"
            ))
            methods.append(ActionDefinition(
                name="activate_cell",
                tool="sap_table_action",
                action_type=ActionTypes.ACTIVATE_CELL,
                description="Double-clicks a cell (navigation)"
            ))
            
        elif subtype == ControlSubtypes.TREE:
            methods.append(ActionDefinition(
                name="click",
                tool="sap_shell_action",
                action_type=ActionTypes.CLICK,
                description="Interacts with shell component"
            ))
            
        elif subtype == ControlSubtypes.TAB:
            methods.append(ActionDefinition(
                name="select",
                tool="sap_interact_field",
                action_type=ActionTypes.SELECT_TAB,
                description="Selects the tab"
            ))
            
        elif subtype == ControlSubtypes.MENU:
            methods.append(ActionDefinition(
                name="select",
                tool="sap_interact_field",
                action_type=ActionTypes.PRESS_BUTTON,
                description="Selects the menu item"
            ))
            
        return methods

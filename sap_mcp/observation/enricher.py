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
        control.actions = [m.tool_name for m in control.supported_methods]
        
        return control

    def _define_methods(self, subtype: str, editable: bool) -> List[ActionDefinition]:
        """
        Maps subtypes to allowed interaction methods.
        """
        methods = []
        
        if subtype == ControlSubtypes.BUTTON:
            methods.append(ActionDefinition(
                name=ActionTypes.PRESS_BUTTON,
                tool_name="sap_shell_action",
                description="Clicks the button"
            ))
            
        elif subtype == ControlSubtypes.TEXT:
            if editable:
                methods.append(ActionDefinition(
                    name=ActionTypes.SET_FIELD,
                    tool_name="sap_interact_field",
                    description="Sets the text value"
                ))
                
        elif subtype == ControlSubtypes.CHECKBOX:
            methods.append(ActionDefinition(
                name=ActionTypes.SET_CHECKBOX,
                tool_name="sap_interact_field",
                description="Checks/Unchecks the box"
            ))
            
        elif subtype == ControlSubtypes.RADIO:
            methods.append(ActionDefinition(
                name=ActionTypes.SELECT_RADIO,
                tool_name="sap_interact_field",
                description="Selects the radio option"
            ))
            
        elif subtype == ControlSubtypes.COMBOBOX:
            methods.append(ActionDefinition(
                name=ActionTypes.SET_FIELD,
                tool_name="sap_interact_field",
                description="Selects an item by Key"
            ))
            
        elif subtype == ControlSubtypes.TABLE:
            methods.append(ActionDefinition(
                name=ActionTypes.SET_CELL_DATA,
                tool_name="sap_table_action",
                description="Writes to a specific cell"
            ))
            methods.append(ActionDefinition(
                name=ActionTypes.TABLE_BATCH_FILL,
                tool_name="sap_table_action",
                description="Fills multiple rows efficiently"
            ))
            
        elif subtype in (ControlSubtypes.GRID, ControlSubtypes.TREE):
            # Generic shell handler for complex shells
            methods.append(ActionDefinition(
                name="click",
                tool_name="sap_shell_action",
                description="Interacts with shell component"
            ))
            
        elif subtype == ControlSubtypes.TAB:
            methods.append(ActionDefinition(
                name=ActionTypes.SELECT_TAB,
                tool_name="sap_interact_field",
                description="Selects the tab"
            ))
            
        return methods

from typing import Any, Dict, Optional
from .base_tool import BaseMcpTool
from ...execution.action_dispatcher import ActionDispatcher
from ...schemas import ActionRequest
from ...core.config import ActionTypes

class SapNavigateTool(BaseMcpTool):
    def __init__(self, action_dispatcher: ActionDispatcher):
        self.action_dispatcher = action_dispatcher

    @property
    def name(self) -> str:
        return "sap_navigate"

    @property
    def description(self) -> str:
        return (
            "PURPOSE: Fast traversal via Transaction Codes or keyboard emulation.\n"
            "WHEN TO USE: Use 'navigate_tcode' for global navigation (e.g. '/nME21N'). "
            "Use 'send_vkey' for keyboard shortcuts: 0 (Enter), 3 (Back), 11 (Save), 12 (Cancel)."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string" },
                "action_type": { "type": "string", "enum": ["navigate_tcode", "send_vkey"] },
                "tcode": { "type": "string", "description": "The T-Code (e.g. VA01). Start with /n to clear current transaction." },
                "vkey": { "type": "integer", "description": "The SAP Virtual Key code.", "default": 0 }
            },
            "required": ["session_id", "action_type"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            request = ActionRequest(
                session_id=arguments["session_id"],
                action_type=arguments["action_type"],
                params={"tcode": arguments.get("tcode"), "vkey": arguments.get("vkey", 0)}
            )
            result = await self.action_dispatcher.execute(request)
            return self._success_response(result.model_dump_json())
        except Exception as e:
            return self._error_response(str(e))

class SapInteractTool(BaseMcpTool):
    def __init__(self, action_dispatcher: ActionDispatcher):
        self.action_dispatcher = action_dispatcher

    @property
    def name(self) -> str:
        return "sap_interact_field"

    @property
    def description(self) -> str:
        return (
            "PURPOSE: Atomic UI interactions with standard controls.\n"
            "WHEN TO USE: Use for GuiTextField, GuiComboBox, GuiCheckBox, and GuiTab."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string" },
                "target_id": { "type": "string", "description": "The absolute SAP ID." },
                "action_type": { "type": "string", "enum": ["set_field", "set_checkbox", "select_tab", "press_button"] },
                "value": { "type": "string", "description": "The input text, boolean checkbox state, or dropdown key." }
            },
            "required": ["session_id", "target_id", "action_type"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            request = ActionRequest(
                session_id=arguments["session_id"],
                target_id=arguments["target_id"],
                action_type=arguments["action_type"],
                params={"value": arguments.get("value")}
            )
            result = await self.action_dispatcher.execute(request)
            return self._success_response(result.model_dump_json())
        except Exception as e:
            return self._error_response(str(e))

class SapTableActionTool(BaseMcpTool):
    def __init__(self, action_dispatcher: ActionDispatcher):
        self.action_dispatcher = action_dispatcher

    @property
    def name(self) -> str:
        return "sap_table_action"

    @property
    def description(self) -> str:
        return (
            "PURPOSE: High-level interaction with GuiTableControl and ALV GridView components.\n"
            "WHEN TO USE: Mandatory for any control of type 'table' or 'grid' identified in observation."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string" },
                "target_id": { "type": "string" },
                "action_type": { "type": "string", "enum": ["set_cell_data", "get_cell_data", "activate_cell", "select_row", "find_row_by_text", "table_batch_fill"] },
                "row": { "type": "integer", "description": "Logical row index starting from 0." },
                "column": { "type": "string", "description": "The technical column name or numeric index." },
                "value": { "type": "string", "description": "Input value or search criterion." },
                "rows": { 
                    "type": "array", 
                    "description": "Used only for table_batch_fill. List of {row, data: {col: val}} objects.",
                    "items": { "type": "object" }
                }
            },
            "required": ["session_id", "target_id", "action_type"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            request = ActionRequest(
                session_id=arguments["session_id"],
                target_id=arguments["target_id"],
                action_type=arguments["action_type"],
                params={
                    "row": arguments.get("row"),
                    "column": arguments.get("column"),
                    "value": arguments.get("value"),
                    "rows": arguments.get("rows")
                }
            )
            result = await self.action_dispatcher.execute(request)
            return self._success_response(result.model_dump_json())
        except Exception as e:
            return self._error_response(str(e))

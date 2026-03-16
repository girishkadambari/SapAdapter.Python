from typing import Any, Dict
from .base_tool import BaseMcpTool
from ...execution.action_dispatcher import ActionDispatcher
from ...schemas import ActionRequest

class SapShellActionTool(BaseMcpTool):
    def __init__(self, action_dispatcher: ActionDispatcher):
        self.action_dispatcher = action_dispatcher

    @property
    def name(self) -> str:
        return "sap_shell_action"

    @property
    def description(self) -> str:
        return (
            "PURPOSE: Interaction with complex shell components (Tree, Toolbar, GridView).\n"
            "WHEN TO USE: Use for tree nodes, toolbar buttons, or clicking specific coordinates in a shell."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string" },
                "target_id": { "type": "string", "description": "The absolute SAP ID of the shell control." },
                "action_type": { 
                    "type": "string", 
                    "enum": ["select_node", "expand_node", "collapse_node", "double_click_node", "node_context_menu", "select_item", "find_node_by_path", "press_button", "click"] 
                },
                "node_key": { "type": "string", "description": "Used for tree actions." },
                "item_name": { "type": "string", "description": "Used for select_item in trees." },
                "path": { "type": "string", "description": "Used for find_node_by_path." },
                "button_id": { "type": "string", "description": "Used for toolbar/context buttons." },
                "x": { "type": "integer", "description": "X coordinate for click action." },
                "y": { "type": "integer", "description": "Y coordinate for click action." }
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
                    "node_key": arguments.get("node_key"),
                    "item_name": arguments.get("item_name"),
                    "path": arguments.get("path"),
                    "button_id": arguments.get("button_id"),
                    "x": arguments.get("x"),
                    "y": arguments.get("y")
                }
            )
            result = await self.action_dispatcher.execute(request)
            return self._success_response(result.model_dump_json())
        except Exception as e:
            return self._error_response(str(e))

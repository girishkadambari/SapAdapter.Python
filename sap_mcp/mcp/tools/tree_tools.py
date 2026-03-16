import json
from typing import Any, Dict, List
from .base_tool import BaseMcpTool
from ...runtime.sap_runtime import SapRuntime

class SapListTreeNodesTool(BaseMcpTool):
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime

    @property
    def name(self) -> str:
        return "sap_list_tree_nodes"

    @property
    def description(self) -> str:
        return "PURPOSE: Recursively list all nodes (keys and text) in an SAP Tree control."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string" },
                "target_id": { "type": "string", "description": "The absolute SAP ID of the Tree control." }
            },
            "required": ["session_id", "target_id"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            session = self.runtime.get_session(arguments["session_id"])
            tree = session.FindById(arguments["target_id"])
            
            # Ensure it's a tree
            if not (hasattr(tree, "Type") and (str(tree.Type) == "GuiTree" or (str(tree.Type) == "GuiShell" and str(tree.SubType) == "Tree"))):
                return self._error_response(f"Control {arguments['target_id']} is not a Tree.")

            lines = []
            node_keys = tree.GetAllNodeKeys()
            if node_keys:
                for i in range(node_keys.Count):
                    key = node_keys(i)
                    text = tree.GetNodeTextByKey(key)
                    lines.append(f"{key} | {text}")

            return self._success_response("\n".join(lines))
        except Exception as e:
            return self._error_response(str(e))

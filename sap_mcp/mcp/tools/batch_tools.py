from typing import Any, Dict, List
from .base_tool import BaseMcpTool
from ...execution.action_dispatcher import ActionDispatcher
from ...schemas import ActionRequest

class SapExecuteBatchTool(BaseMcpTool):
    def __init__(self, action_dispatcher: ActionDispatcher):
        self.action_dispatcher = action_dispatcher

    @property
    def name(self) -> str:
        return "sap_execute_batch"

    @property
    def description(self) -> str:
        return (
            "PURPOSE: Atomic execution of multiple actions in a single request.\n"
            "WHEN TO USE: Use to perform a sequence of safe interactions (e.g. filling multiple fields in a form)."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string" },
                "actions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tool": { "type": "string" },
                            "action_type": { "type": "string" },
                            "target_id": { "type": "string" },
                            "params": { "type": "object" }
                        },
                        "required": ["tool", "action_type"]
                    }
                }
            },
            "required": ["session_id", "actions"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            sid = arguments["session_id"]
            action_dicts = arguments["actions"]
            
            requests = []
            for ad in action_dicts:
                # Map parameters (simplified version of the original logic)
                params = ad.get("params", {})
                for k in ["row", "column", "value", "tcode", "vkey"]:
                    if k in ad and k not in params:
                        params[k] = ad[k]

                requests.append(ActionRequest(
                    session_id=sid,
                    target_id=ad.get("target_id"),
                    action_type=ad["action_type"],
                    params=params
                ))
            
            results = await self.action_dispatcher.execute_batch(sid, requests)
            summary = f"Executed {len(results)}/{len(requests)} actions.\n" + "\n".join([r.model_dump_json() for r in results])
            return self._success_response(summary)
        except Exception as e:
            return self._error_response(str(e))

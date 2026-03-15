from typing import Any, Dict
from .base_tool import BaseMcpTool
from ...runtime.sap_runtime import SapRuntime

class SapListSessionsTool(BaseMcpTool):
    """
    Tool to discovery active SAP GUI windows.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime

    @property
    def name(self) -> str:
        return "sap_list_sessions"

    @property
    def description(self) -> str:
        return (
            "PURPOSE: Discovery of active SAP GUI windows.\n"
            "WHEN TO USE: Always call this first when starting a session to identify connection and session indices. "
            "The resulting 'sessionId' (e.g. '0-0') must be passed to all subsequent calls."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            sessions = self.runtime.list_sessions()
            return self._success_response(str(sessions))
        except Exception as e:
            return self._error_response(str(e))

import json
from typing import Any, Dict
from .base_tool import BaseMcpTool
from ...observation.screen_observation_builder import ScreenObservationBuilder
from ...execution.action_dispatcher import ActionDispatcher
from ...schemas import ActionRequest
from ...core.config import ActionTypes

class SapGetSapContextTool(BaseMcpTool):
    def __init__(self, observation_builder: ScreenObservationBuilder):
        self.observation_builder = observation_builder

    @property
    def name(self) -> str:
        return "get_sap_context"

    @property
    def description(self) -> str:
        return "PURPOSE: Fast retrieval of current SAP session context."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": { "session_id": { "type": "string" } },
            "required": ["session_id"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            context = await self.observation_builder.build_context(arguments.get("session_id"))
            return self._success_response(json.dumps(context))
        except Exception as e:
            return self._error_response(str(e))

class SapGetStatusAndIncompletionTool(BaseMcpTool):
    def __init__(self, observation_builder: ScreenObservationBuilder):
        self.observation_builder = observation_builder

    @property
    def name(self) -> str:
        return "get_status_and_incompletion"

    @property
    def description(self) -> str:
        return "PURPOSE: Comprehensive check of document status and incompletion logs."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": { "session_id": { "type": "string" } },
            "required": ["session_id"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            verification = await self.observation_builder.build_verification(arguments.get("session_id"))
            return self._success_response(json.dumps(verification))
        except Exception as e:
            return self._error_response(str(e))

class SapSearchHelpSelectTool(BaseMcpTool):
    def __init__(self, action_dispatcher: ActionDispatcher):
        self.action_dispatcher = action_dispatcher

    @property
    def name(self) -> str:
        return "sap_search_help_select"

    @property
    def description(self) -> str:
        return "PURPOSE: Semantic selection from an SAP Search Help (F4) hit list."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string" },
                "row": { "type": "integer", "default": 0 },
                "value": { "type": "string" }
            },
            "required": ["session_id"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            request = ActionRequest(
                session_id=arguments["session_id"],
                action_type=ActionTypes.SEARCH_HELP_SELECT,
                params={
                    "row": arguments.get("row", 0),
                    "value": arguments.get("value")
                }
            )
            result = await self.action_dispatcher.execute(request)
            return self._success_response(result.model_dump_json())
        except Exception as e:
            return self._error_response(str(e))

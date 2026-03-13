from typing import Any, Dict, List, Optional
from loguru import logger

from ..runtime.sap_runtime import SapRuntime
from ..observation.screen_observation_builder import ScreenObservationBuilder
from ..execution.action_dispatcher import ActionDispatcher
from ..extraction.entity_extractor import EntityExtractor
from ..schemas.action import ActionRequest

from .tool_definitions import get_tool_definitions

class McpAdapter:
    """
    Adapter that bridges MCP protocol calls to internal SAP services.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime
        self.observation_builder = ScreenObservationBuilder(runtime)
        self.action_dispatcher = ActionDispatcher(runtime)
        self.entity_extractor = EntityExtractor()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Returns the list of available MCP tools.
        """
        return get_tool_definitions()

    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches an MCP tool call to the appropriate internal service.
        """
        try:
            if name == "list_sessions":
                sessions = self.runtime.list_sessions()
                return {"content": [{"type": "text", "text": str(sessions)}]}

            elif name == "observe_screen":
                sid = arguments.get("session_id")
                include_ss = arguments.get("include_screenshot", False)
                observation = await self.observation_builder.build(sid, include_screenshot=include_ss)
                return {"content": [{"type": "text", "text": observation.model_dump_json()}]}

            elif name == "execute_action":
                request = ActionRequest(
                    session_id=arguments["session_id"],
                    target_id=arguments["target_id"],
                    action_type=arguments["action_type"],
                    params=arguments.get("params", {})
                )
                result = await self.action_dispatcher.execute(request)
                return {"content": [{"type": "text", "text": result.model_dump_json()}]}

            elif name == "extract_entity":
                sid = arguments["session_id"]
                entity_type = arguments["entity_type"]
                observation = await self.observation_builder.build(sid)
                extraction = self.entity_extractor.extract_entity(observation, entity_type)
                return {"content": [{"type": "text", "text": extraction.model_dump_json()}]}

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Error executing MCP tool {name}: {str(e)}")
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Error: {str(e)}"}]
            }

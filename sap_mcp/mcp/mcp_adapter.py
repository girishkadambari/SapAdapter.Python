from typing import Any, Dict, List, Optional
from loguru import logger

from ..runtime.sap_runtime import SapRuntime
from ..observation.screen_observation_builder import ScreenObservationBuilder
from ..execution.action_dispatcher import ActionDispatcher
from ..extraction.entity_extractor import EntityExtractor
from ..schemas import ActionRequest

from .tools.registry import ToolRegistry
from .tools.session_tools import SapListSessionsTool
from .tools.screen_tools import SapGetScreenSummaryTool, SapInspectControlTool, SapCaptureVisualTool, SapObserveScreenTool
from .tools.action_tools import SapNavigateTool, SapInteractTool, SapTableActionTool
from .tools.shell_tools import SapShellActionTool
from .tools.batch_tools import SapExecuteBatchTool
from .tools.context_tools import SapGetSapContextTool, SapGetStatusAndIncompletionTool, SapSearchHelpSelectTool
from .tools.tree_tools import SapListTreeNodesTool

class McpAdapter:
    """
    Adapter that bridges MCP protocol calls to internal SAP services.
    Refactored to use a Command Pattern via ToolRegistry.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime
        self.observation_builder = ScreenObservationBuilder(runtime)
        self.action_dispatcher = ActionDispatcher(runtime)
        self.entity_extractor = EntityExtractor()
        
        self.registry = ToolRegistry()
        self._register_tools()

    def _register_tools(self):
        """Initializes and registers all MCP tools."""
        # Session Tools
        self.registry.register(SapListSessionsTool(self.runtime))
        
        # Screen Tools
        self.registry.register(SapGetScreenSummaryTool(self.observation_builder))
        self.registry.register(SapInspectControlTool(self.observation_builder))
        self.registry.register(SapCaptureVisualTool(self.observation_builder))
        self.registry.register(SapObserveScreenTool(self.observation_builder))
        
        # Action Tools
        self.registry.register(SapNavigateTool(self.action_dispatcher))
        self.registry.register(SapInteractTool(self.action_dispatcher))
        self.registry.register(SapTableActionTool(self.action_dispatcher))
        self.registry.register(SapShellActionTool(self.action_dispatcher))
        
        # Batch Tools
        self.registry.register(SapExecuteBatchTool(self.action_dispatcher))
        
        # Context & Help Tools
        self.registry.register(SapGetSapContextTool(self.observation_builder))
        self.registry.register(SapGetStatusAndIncompletionTool(self.observation_builder))
        self.registry.register(SapSearchHelpSelectTool(self.action_dispatcher))
        self.registry.register(SapListTreeNodesTool(self.runtime))

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Returns the list of available MCP tools from the registry.
        """
        return self.registry.list_tool_definitions()

    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches an MCP tool call to the registry.
        """
        try:
            # Special case for extract_entity (domain)
            if name == "extract_entity":
                sid = arguments.get("session_id")
                entity_type = arguments["entity_type"]
                observation = await self.observation_builder.build(sid)
                extraction = self.entity_extractor.extract_entity(observation, entity_type)
                return extraction.model_dump_json() if hasattr(extraction, 'model_dump_json') else str(extraction)
                
            return await self.registry.call_tool(name, arguments)
        except Exception as e:
            logger.error(f"Error executing MCP tool {name}: {str(e)}")
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Error: {str(e)}"}]
            }

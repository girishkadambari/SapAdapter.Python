from typing import List, Dict, Type, Any, Optional
from .base_tool import BaseMcpTool
from loguru import logger

class ToolRegistry:
    """
    Registry for managing and discovering MCP tool implementations.
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseMcpTool] = {}

    def register(self, tool: BaseMcpTool):
        """Registers a tool instance."""
        if tool.name in self._tools:
            logger.warning(f"Overwriting tool registration for: {tool.name}")
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseMcpTool]:
        """Retrieves a tool instance by name."""
        return self._tools.get(name)

    def list_tool_definitions(self) -> List[Dict[str, Any]]:
        """Aggregates all tool definitions for the MCP list_tools call."""
        return [tool.get_definition() for tool in self._tools.values()]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Delegates the tool call to the appropriate tool instance."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        
        return await tool.execute(arguments)

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from loguru import logger

class BaseMcpTool(ABC):
    """
    Abstract base class for all SAP MCP tools.
    Follows the Command Pattern for predictable execution.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The technical name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """The tool description for the AI agent."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """The JSON-RPC input schema for the tool."""
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the tool logic with the provided arguments.
        Returns a dictionary formatted for the MCP response content.
        """
        pass

    def get_definition(self) -> Dict[str, Any]:
        """Returns the complete MCP tool definition."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Standardized error response for tools."""
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Error in {self.name}: {message}"}]
        }

    def _success_response(self, text: str) -> Dict[str, Any]:
        """Standardized success response for tools."""
        return {
            "content": [{"type": "text", "text": text}]
        }

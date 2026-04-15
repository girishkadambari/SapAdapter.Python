import pytest
from sap_mcp.mcp.tools.registry import ToolRegistry
from sap_mcp.mcp.tools.base_tool import BaseMcpTool
from typing import Dict, Any

class MockTool(BaseMcpTool):
    @property
    def name(self) -> str:
        return "mock_tool"
    
    @property
    def description(self) -> str:
        return "A mock tool for testing"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self._success_response("Mock Success")

@pytest.mark.asyncio
async def test_tool_registry():
    registry = ToolRegistry()
    tool = MockTool()
    
    registry.register(tool)
    
    # Test discovery
    definitions = registry.list_tool_definitions()
    assert len(definitions) == 1
    assert definitions[0]["name"] == "mock_tool"
    
    # Test execution
    result = await registry.call_tool("mock_tool", {})
    assert result["content"][0]["text"] == "Mock Success"

@pytest.mark.asyncio
async def test_registry_unknown_tool():
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="Unknown tool: missing"):
        await registry.call_tool("missing", {})

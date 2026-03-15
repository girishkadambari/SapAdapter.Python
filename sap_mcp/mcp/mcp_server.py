import json
from typing import Any, Dict, Optional
from loguru import logger
from .mcp_adapter import McpAdapter

class McpServer:
    """
    Standard Model Context Protocol (MCP) server logic.
    Handles JSON-RPC 2.0 requests for tools and resources.
    """
    
    def __init__(self, adapter: McpAdapter):
        self.adapter = adapter

    async def handle_message(self, message: str) -> Optional[str]:
        """
        Processes an incoming MCP message and returns a JSON-RPC response.
        """
        try:
            data = json.loads(message)
            if not isinstance(data, dict):
                return None
                
            msg_id = data.get("id")
            method = data.get("method")
            params = data.get("params", {})

            # MCP JSON-RPC Routing
            if method == "initialize":
                return self._make_response(msg_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "sap-mcp",
                        "version": "1.0.0"
                    }
                })

            elif method == "ping":
                return self._make_response(msg_id, {})

            elif method == "tools/list":
                tools = await self.adapter.list_tools()
                return self._make_response(msg_id, {"tools": tools})

            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments", {})
                result = await self.adapter.handle_call_tool(name, args)
                return self._make_response(msg_id, result)

            elif method == "resources/list":
                # Resources placeholder
                return self._make_response(msg_id, {"resources": []})

            elif method == "notifications/initialized":
                # Ignore initialization notifications
                return None

            else:
                logger.warning(f"Unsupported MCP method: {method}")
                return self._make_error(msg_id, -32601, f"Method not found: {method}")

        except json.JSONDecodeError:
            return self._make_error(None, -32700, "Parse error")
        except Exception as e:
            logger.exception("Internal error during MCP message handling")
            return self._make_error(data.get("id"), -32603, str(e))

    def _make_response(self, msg_id: Any, result: Any) -> str:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result
        })

    def _make_error(self, msg_id: Any, code: int, message: str) -> str:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": code,
                "message": message
            }
        })

import asyncio
import json
import os
import pythoncom
from loguru import logger
import websockets
from http import HTTPStatus

from sap_mcp.utils.logger import setup_logger
from sap_mcp.runtime.sap_runtime import SapRuntime
from sap_mcp.mcp.mcp_adapter import McpAdapter
from sap_mcp.mcp.mcp_server import McpServer
from sap_mcp.server.router import CommandRouter

# This adapter allows Postman (HTTP) to interact with the WebSocket-based MCP server
# by hijacking the 'process_request' hook in the websockets library.

setup_logger()

class PostmanTestBridge:
    def __init__(self, runtime: SapRuntime, mcp_server: McpServer, router: CommandRouter):
        self.runtime = runtime
        self.mcp_server = mcp_server
        self.router = router

    async def process_request(self, path, request_headers):
        """
        Intercepts HTTP requests before they upgrade to WebSockets.
        This allows Postman to send regular POST requests to the same port.
        """
        # We only care about POST requests to /mcp or /legacy
        # However, 'websockets' process_request doesn't easily give us the body
        # So we will use a dedicated tiny AIOHTTP-like server if body is needed.
        # Since 'websockets' doesn't provide the body in process_request, 
        # we'll implement a separate minimal HTTP server using asyncio.
        return None 

async def handle_http_request(reader, writer, mcp_server, router, runtime):
    """
    Minimalistic Async HTTP POST handler for Postman.
    """
    try:
        data = await reader.read(4096)
        if not data:
            return
            
        request_text = data.decode()
        lines = request_text.split("\r\n")
        if not lines:
            return
            
        first_line = lines[0].split()
        if len(first_line) < 2:
            return
            
        method, path = first_line[0], first_line[1]
        
        if method == "POST":
            # Extract body
            parts = request_text.split("\r\n\r\n", 1)
            body = parts[1] if len(parts) > 1 else ""
            
            response_body = ""
            if path == "/mcp":
                response_body = await mcp_server.handle_message(body)
            elif path == "/legacy":
                data = json.loads(body)
                req_type = data.get("type")
                payload = data.get("payload", {})
                result = await router.handle(req_type, payload, context={})
                response_body = json.dumps({"ok": True, "payload": result})
            else:
                response_body = json.dumps({"error": "Not Found"})
                
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Connection: close\r\n\r\n"
                f"{response_body}"
            )
        elif method == "GET" and path == "/health":
            response_body = json.dumps({"status": "ok", "mode": "test-adapter"})
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                f"Connection: close\r\n\r\n"
                f"{response_body}"
            )
        else:
            response = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n"

        writer.write(response.encode())
        await writer.drain()
    except Exception as e:
        logger.error(f"Test Bridge Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    logger.info("Starting Postman Test Adapter (HTTP Bridge)...")
    
    runtime = SapRuntime()
    mcp_adapter = McpAdapter(runtime)
    mcp_server = McpServer(mcp_adapter)
    
    # Setup legacy handlers (bridged from main.py)
    router = CommandRouter()
    from main import (
        list_sessions_handler, 
        capture_snapshot_handler, 
        execute_command_handler,
        health_check_handler,
        attach_session_handler
    )
    router.register("healthCheck", health_check_handler)
    router.register("listSessions", list_sessions_handler)
    router.register("attachSession", attach_session_handler)
    router.register("captureSnapshot", capture_snapshot_handler)
    router.register("executeCommand", execute_command_handler)

    port = int(os.getenv("TEST_PORT", 8788))
    server = await asyncio.start_server(
        lambda r, w: handle_http_request(r, w, mcp_server, router, runtime),
        "0.0.0.0", port
    )
    
    logger.info(f"Postman Test Bridge listening on http://localhost:{port}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

import json
import asyncio
import websockets
from loguru import logger
from typing import Any, Optional

class WebSocketServer:
    """
    WebSocket server supporting both legacy JSON-RPC and MCP protocols.
    """
    def __init__(self, host: str, port: int, router: Any):
        self.host = host
        self.port = port
        self.router = router
        self.clients = set()
        self.mcp_server = None

    async def start(self):
        logger.info(f"Starting SAP Server on {self.host}:{self.port}...")
        async with websockets.serve(self._handle_client, self.host, self.port):
            await asyncio.Future()

    async def _handle_client(self, websocket):
        client_info = websocket.remote_address
        logger.info(f"Client connected: {client_info}")
        self.clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # 1. MCP Protocol Handle
                    if isinstance(data, dict) and (data.get("jsonrpc") == "2.0" or "method" in data):
                        if self.mcp_server:
                            logger.debug(f"MCP Call: {data.get('method')}")
                            response_str = await self.mcp_server.handle_message(message)
                            if response_str:
                                await websocket.send(response_str)
                            continue

                    # 2. Legacy Protocol Handle
                    req_id = data.get("id", "none")
                    req_type = data.get("type", "unknown")
                    logger.debug(f"Legacy Request: {req_type} ({req_id})")
                    
                    try:
                        result = await self.router.handle(req_type, data.get("payload", {}), context={"ws": websocket})
                        response = {
                            "id": req_id,
                            "ok": True,
                            "payload": result
                        }
                    except Exception as e:
                        logger.error(f"Handler error: {str(e)}")
                        response = {
                            "id": req_id,
                            "ok": False,
                            "error": {"code": "HANDLER_ERROR", "message": str(e)}
                        }
                    
                    await websocket.send(json.dumps(response))

                except json.JSONDecodeError:
                    logger.warning("Invalid JSON received")
                except Exception as e:
                    logger.error(f"Message handling error: {str(e)}")

        finally:
            logger.info(f"Client disconnected: {client_info}")
            if websocket in self.clients:
                self.clients.remove(websocket)

    async def broadcast(self, event_name: str, data: Any):
        if not self.clients:
            return
        payload = json.dumps({"type": "event", "event": event_name, "payload": data})
        await asyncio.gather(
            *[client.send(payload) for client in self.clients],
            return_exceptions=True
        )

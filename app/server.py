# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/server.py
import json
import asyncio
import websockets
from loguru import logger
from .models.protocol import RequestModel, ResponseModel
from .commands.router import CommandRouter

class WebSocketServer:
    """
    Production-quality WebSocket server for the SAP Adapter.
    """
    def __init__(self, host: str, port: int, router: CommandRouter):
        self.host = host
        self.port = port
        self.router = router
        self.clients = set()

    async def start(self):
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}...")
        async with websockets.serve(self._handle_client, self.host, self.port):
            await asyncio.Future()  # run forever

    async def _handle_client(self, websocket):
        logger.info(f"Client connected: {websocket.remote_address}")
        self.clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    request = RequestModel(**data)
                    logger.debug(f"Request: {request.command} ({request.id})")
                    
                    response = await self.router.handle(request, context={"ws": websocket})
                    await websocket.send(response.model_dump_json())
                except json.JSONDecodeError:
                    logger.warning("Received invalid JSON")
                except Exception as e:
                    logger.error(f"Error handling message: {str(e)}")
        finally:
            logger.info(f"Client disconnected: {websocket.remote_address}")
            self.clients.remove(websocket)

    async def broadcast(self, event_name: str, data: Any):
        """
        Broadcasts an event to all connected clients.
        """
        if not self.clients:
            return
            
        payload = json.dumps({"event": event_name, "data": data})
        await asyncio.gather(
            *[client.send(payload) for client in self.clients],
            return_exceptions=True
        )

# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/commands/router.py
import asyncio
from loguru import logger
from typing import Dict, Any, Callable, Awaitable
from ..models.protocol import RequestModel, ResponseModel

class CommandRouter:
    """
    Routes incoming JSON commands to the appropriate handler functions.
    Matches the 'router' pattern from the C# version.
    """
    
    def __init__(self):
        self.handlers: Dict[str, Callable[[Any, Dict[str, Any]], Awaitable[Dict[str, Any]]]] = {}

    def register(self, command: str, handler: Callable):
        self.handlers[command] = handler
        logger.debug(f"Registered handler for command: {command}")

    async def handle(self, request: RequestModel, context: Any) -> ResponseModel:
        """
        Routes the request and returns a standardized response.
        """
        if request.type not in self.handlers:
            logger.warning(f"Unknown command: {request.type}")
            return ResponseModel(
                id=request.id,
                ok=False,
                error={
                    "code": "UNKNOWN_COMMAND",
                    "message": f"Unknown command: {request.type}"
                }
            )

        try:
            handler = self.handlers[request.type]
            result = await handler(context, request.payload or {})
            return ResponseModel(id=request.id, ok=True, payload=result)
        except Exception as e:
            logger.exception(f"Error handling command {request.type}")
            return ResponseModel(
                id=request.id,
                ok=False,
                error={
                    "code": "HANDLER_ERROR",
                    "message": str(e)
                }
            )

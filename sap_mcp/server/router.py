import asyncio
from loguru import logger
from typing import Dict, Any, Callable, Awaitable

class CommandRouter:
    """
    Routes incoming JSON commands to the appropriate handler functions.
    Simplified version of the legacy router.
    """
    
    def __init__(self):
        self.handlers: Dict[str, Callable[[Any, Dict[str, Any]], Awaitable[Dict[str, Any]]]] = {}

    def register(self, command: str, handler: Callable):
        self.handlers[command] = handler
        logger.debug(f"Registered handler for command: {command}")

    async def handle(self, command_type: str, payload: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Routes the request and returns a raw dictionary result.
        """
        if command_type not in self.handlers:
            raise ValueError(f"Unknown command: {command_type}")

        handler = self.handlers[command_type]
        return await handler(context, payload)

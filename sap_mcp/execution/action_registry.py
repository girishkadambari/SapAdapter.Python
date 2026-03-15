from typing import Dict, Type
from .handlers.base_handler import ActionHandler
from loguru import logger

class ActionRegistry:
    """
    Registry for action handlers to avoid giant if/else dispatch blocks.
    """
    def __init__(self):
        self._handlers: Dict[str, Type[ActionHandler]] = {}

    def register(self, action_type: str, handler_cls: Type[ActionHandler]):
        """Register a handler class for a specific action type."""
        self._handlers[action_type] = handler_cls
        logger.debug(f"Registered ActionHandler for: {action_type}")

    def get_handler_class(self, action_type: str) -> Type[ActionHandler]:
        """Retrieve the handler class for the given action type."""
        if action_type not in self._handlers:
            raise ValueError(f"No handler registered for action type: {action_type}")
        return self._handlers[action_type]

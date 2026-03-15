from typing import Dict, Type
from ..core.config import ActionTypes
from .handlers.base_handler import ActionHandler
from .handlers.field_handler import FieldHandler
from .handlers.button_handler import ButtonHandler
from .handlers.navigation_handler import NavigationHandler
from .handlers.table_handler import TableHandler
from .handlers.search_help_handler import SearchHelpHandler
from .handlers.shell_handler import ShellHandler

class ActionRegistry:
    """
    Registry for action handlers.
    Maps ActionType strings to ActionHandler classes.
    """
    def __init__(self):
        self._handlers: Dict[str, Type[ActionHandler]] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Registers the standard set of handlers."""
        defaults = {
            ActionTypes.SET_FIELD: FieldHandler,
            ActionTypes.SET_CHECKBOX: FieldHandler,
            ActionTypes.SELECT_RADIO: FieldHandler,
            ActionTypes.PRESS_BUTTON: ButtonHandler,
            ActionTypes.SELECT_TAB: ButtonHandler,
            ActionTypes.NAVIGATE_TCODE: NavigationHandler,
            ActionTypes.SEND_VKEY: NavigationHandler,
            ActionTypes.SET_CELL_DATA: TableHandler,
            ActionTypes.GET_CELL_DATA: TableHandler,
            ActionTypes.SELECT_ROW: TableHandler,
            ActionTypes.FIND_ROW_BY_TEXT: TableHandler,
            ActionTypes.TABLE_BATCH_FILL: TableHandler,
            ActionTypes.CLICK: ShellHandler
        }
        for action_type, handler_cls in defaults.items():
            self.register(action_type, handler_cls)

    def register(self, action_type: str, handler_cls: Type[ActionHandler]):
        """Register a handler class for a specific action type."""
        self._handlers[action_type] = handler_cls

    def get_handler_class(self, action_type: str) -> Type[ActionHandler]:
        """Returns the handler class for the given action type."""
        if action_type not in self._handlers:
            raise ValueError(f"No handler registered for action type: {action_type}")
        return self._handlers[action_type]

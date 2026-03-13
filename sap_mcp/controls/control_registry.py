from typing import Any, Dict, Optional, Type
from .base_handler import BaseControlHandler

class ControlRegistry:
    """
    Registry for mapping SAP GUI control types to specialized handlers.
    """
    
    def __init__(self):
        self._handlers: Dict[str, BaseControlHandler] = {}
        self._default_handler: Optional[BaseControlHandler] = None

    def register(self, sap_type: str, handler: BaseControlHandler):
        """
        Registers a handler for a specific SAP GUI type.
        """
        self._handlers[sap_type] = handler

    def set_default_handler(self, handler: BaseControlHandler):
        """
        Sets a fallback handler for unknown types.
        """
        self._default_handler = handler

    def get_handler(self, control: Any) -> BaseControlHandler:
        """
        Returns the appropriate handler for a given SAP control.
        """
        sap_type = str(control.Type)
        handler = self._handlers.get(sap_type)
        
        if not handler:
            # Try to find a handler that identifies this control
            for h in self._handlers.values():
                if h.identify(control):
                    return h
                    
    @classmethod
    def create_with_core_handlers(cls) -> 'ControlRegistry':
        """
        Factory method to create a registry with all core handlers pre-registered.
        """
        from .field_handler import FieldHandler
        from .button_handler import ButtonHandler
        from .tab_handler import TabHandler
        from .menu_handler import MenuHandler
        from .modal_handler import ModalHandler
        from .table_handler import TableHandler
        from .grid_handler import GridHandler
        from .tree_handler import TreeHandler
        from .shell_handler import ShellHandler

        registry = cls()
        
        # Simple types
        fh = FieldHandler()
        registry.register("GuiTextField", fh)
        registry.register("GuiCTextField", fh)
        registry.register("GuiPasswordField", fh)
        registry.register("GuiCheckBox", fh)
        registry.register("GuiRadioButton", fh)
        
        registry.register("GuiButton", ButtonHandler())
        registry.register("GuiTab", TabHandler())
        registry.register("GuiMenu", MenuHandler())
        registry.register("GuiMenuBar", MenuHandler())
        registry.register("GuiModalWindow", ModalHandler())
        
        # Structured types
        registry.register("GuiTableControl", TableHandler())
        registry.register("GuiGridView", GridHandler())
        registry.register("GuiTree", TreeHandler())
        registry.register("GuiShell", ShellHandler())
        
        return registry

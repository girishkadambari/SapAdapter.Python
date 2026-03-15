from loguru import logger
from typing import Any
from ...schemas import ActionRequest, ActionResult
from ...core.config import ActionTypes, SapGuiTypes, Config
from .base_handler import ActionHandler

class SearchHelpHandler(ActionHandler):
    """
    Handler for semantic Search Help (F4) interactions.
    """
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        action = request.action_type
        
        if action == ActionTypes.SEARCH_HELP_SELECT:
            return await self._select_entry(session, request)
        
        raise ValueError(f"Action {action} not supported by SearchHelpHandler")

    async def _select_entry(self, session: Any, request: ActionRequest) -> ActionResult:
        row = request.params.get("row", 0)
        try:
            win = session.ActiveWindow
            # Try to find a selection control
            list_ctrl = self._find_list_control(win)
            
            if list_ctrl:
                if list_ctrl.Type == SapGuiTypes.GRID_VIEW:
                    list_ctrl.doubleClickRow(row)
                elif list_ctrl.Type == SapGuiTypes.TABLE_CONTROL:
                    list_ctrl.getAbsoluteRow(row).selected = True
                    session.sendVKey(Config.DEFAULT_VKEY_ENTER)
                
                return ActionResult(success=True, action_type=request.action_type, message=f"Selected row {row}")
            
            # Fallback for Legacy Lists
            win.setFocus()
            for _ in range(row):
                session.sendVKey(2) # Down Arrow
            
            session.sendVKey(Config.DEFAULT_VKEY_ENTER)
            
            return ActionResult(success=True, action_type=request.action_type, message=f"Selected row {row} (fallback)")
            
        except Exception as e:
            logger.error(f"Search help error: {e}")
            return ActionResult(success=False, action_type=request.action_type, error=str(e))

    def _find_list_control(self, container: Any) -> Any:
        if not container: return None
        if container.Type in (SapGuiTypes.GRID_VIEW, SapGuiTypes.TABLE_CONTROL):
            return container
            
        if hasattr(container, "Children"):
            for i in range(container.Children.Count):
                found = self._find_list_control(container.Children.Item(i))
                if found: return found
        return None

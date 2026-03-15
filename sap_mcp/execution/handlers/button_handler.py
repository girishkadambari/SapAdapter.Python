from typing import Any
from ...schemas import ActionRequest, ActionResult
from .base_handler import ActionHandler
from loguru import logger

class ButtonHandler(ActionHandler):
    """
    Handles button presses in SAP GUI.
    Supports action: `press_button`
    """
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        target_id = self._normalize_target_id(request.target_id)
        
        try:
            target = session.FindById(target_id)
            if request.action_type == "select_tab" or target.Type == "GuiTab":
                target.Select()
            else:
                target.Press()
            logger.info(f"Interacted with button/tab: {target_id}")
            
            return ActionResult(
                success=True,
                action_type=request.action_type,
                target_id=request.target_id,
                message="Button pressed successfully"
            )
        except Exception as e:
            logger.error(f"Failed to press button {target_id}: {str(e)}")
            return ActionResult(
                success=False,
                action_type=request.action_type,
                target_id=request.target_id,
                error=str(e)
            )

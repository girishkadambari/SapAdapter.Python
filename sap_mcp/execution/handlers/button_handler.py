from typing import Any
from loguru import logger
from ...schemas import ActionRequest, ActionResult
from ...core.config import ActionTypes, SapGuiTypes
from .base_handler import ActionHandler

class ButtonHandler(ActionHandler):
    """
    Handles button presses and tab selections in SAP GUI.
    """
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        target_id = self._normalize_target_id(request.target_id)
        action = request.action_type
        
        try:
            target = session.FindById(target_id)
            
            if action == ActionTypes.SELECT_TAB or target.Type == SapGuiTypes.TAB:
                target.Select()
            elif action == ActionTypes.PRESS_BUTTON:
                target.Press()
            else:
                # Fallback for generic press if needed
                if hasattr(target, "Press"):
                    target.Press()
                else:
                    target.Select()
                    
            logger.info(f"Interacted with {target.Type}: {target_id}")
            
            return ActionResult(
                success=True,
                action_type=action,
                target_id=request.target_id,
                message=f"Action {action} completed successfully"
            )
        except Exception as e:
            logger.error(f"Failed to interact with button {target_id}: {str(e)}")
            return ActionResult(
                success=False,
                action_type=action,
                target_id=request.target_id,
                error=str(e)
            )

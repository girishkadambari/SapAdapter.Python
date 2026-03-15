from typing import Any
from loguru import logger
from ...schemas import ActionRequest, ActionResult
from ...core.config import Config, ActionTypes
from .base_handler import ActionHandler

class NavigationHandler(ActionHandler):
    """
    Handles global navigation actions like VKeys and T-Code navigation.
    """
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        action = request.action_type
        params = request.params or {}
        
        try:
            if action == ActionTypes.SEND_VKEY:
                vkey = int(params.get("vkey", Config.DEFAULT_VKEY_ENTER))
                session.ActiveWindow.sendVKey(vkey)
                logger.info(f"Sent VKey: {vkey}")
                
            elif action == ActionTypes.NAVIGATE_TCODE:
                tcode = params.get("tcode")
                if not tcode:
                    raise ValueError("navigate_tcode requires 'tcode' parameter")
                
                # Check for blocking modals
                modal = self.runtime.modal_guard.detect(session)
                if modal:
                    logger.warning(f"Navigation blocked by modal: {modal.title}")
                    return ActionResult(
                        success=False,
                        action_type=action,
                        target_id=request.target_id,
                        error=f"Navigation blocked by modal dialog: '{modal.title}'."
                    )
                
                # Command field navigation
                cmd_field = session.FindById("wnd[0]/tbar[0]/okcd")
                cmd_field.Text = tcode
                session.ActiveWindow.sendVKey(Config.DEFAULT_VKEY_ENTER)
                logger.info(f"Navigated to T-Code: {tcode}")
                
            else:
                raise ValueError(f"Unknown navigation action: {action}")
                
            return ActionResult(
                success=True,
                action_type=action,
                target_id=request.target_id,
                message=f"Navigation action {action} completed"
            )
        except Exception as e:
            logger.error(f"Navigation error: {str(e)}")
            return ActionResult(
                success=False,
                action_type=action,
                target_id=request.target_id,
                error=str(e)
            )

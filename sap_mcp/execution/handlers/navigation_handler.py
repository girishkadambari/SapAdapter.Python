from typing import Any
from ...schemas import ActionRequest, ActionResult
from .base_handler import ActionHandler
from loguru import logger

class NavigationHandler(ActionHandler):
    """
    Handles global navigation actions like VKeys and T-Code navigation.
    Supports actions: `send_vkey`, `navigate_tcode`
    """
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        try:
            if request.action_type == "send_vkey":
                vkey = int(request.params.get("vkey", 0))
                session.ActiveWindow.sendVKey(vkey)
                logger.info(f"Sent VKey: {vkey}")
                
            elif request.action_type == "navigate_tcode":
                tcode = request.params.get("tcode")
                if not tcode:
                    raise ValueError("navigate_tcode requires 'tcode' parameter")
                
                # MODAL RESILIENCE: Check for blocking modals before navigation
                session_id = request.session_id
                runtime_session = self.runtime.get_session(session_id)
                modal = self.runtime.modal_guard.detect(runtime_session)
                if modal:
                    logger.warning(f"Navigation blocked by modal: {modal.title}")
                    return ActionResult(
                        success=False,
                        action_type=request.action_type,
                        target_id=request.target_id,
                        error=f"Navigation blocked by modal dialog: '{modal.title}'. Close the modal before navigating."
                    )
                
                # Use standard command field navigation
                cmd_field = runtime_session.FindById("wnd[0]/tbar[0]/okcd")
                cmd_field.Text = tcode
                runtime_session.ActiveWindow.sendVKey(0)  # Press Enter
                logger.info(f"Navigated to T-Code: {tcode}")
                
            else:
                raise ValueError(f"Unknown navigation action: {request.action_type}")
                
            return ActionResult(
                success=True,
                action_type=request.action_type,
                target_id=request.target_id,
                message=f"Navigation action {request.action_type} completed successfully"
            )
        except Exception as e:
            logger.error(f"Failed navigation action {request.action_type}: {str(e)}")
            return ActionResult(
                success=False,
                action_type=request.action_type,
                target_id=request.target_id,
                error=str(e)
            )

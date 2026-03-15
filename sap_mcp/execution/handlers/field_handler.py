from typing import Any
from loguru import logger
from ...schemas import ActionRequest, ActionResult
from ...core.config import ActionTypes, SapGuiTypes
from .base_handler import ActionHandler

class FieldHandler(ActionHandler):
    """
    Handles text fields, checkboxes, and radio buttons.
    Supports actions: `set_field`, `set_checkbox`, `select_radio`
    """
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        target_id = self._normalize_target_id(request.target_id)
        value = request.params.get("value")
        
        try:
            target = session.FindById(target_id)
            old_value = self._get_value(target)
            
            action = request.action_type
            
            if action == ActionTypes.SET_FIELD:
                if target.Type == SapGuiTypes.COMBOBOX:
                    target.Key = str(value)
                else:
                    target.Text = str(value)
            elif action == ActionTypes.SET_CHECKBOX:
                if hasattr(target, "Key"):
                    target.Key = value
                else:
                    target.Selected = bool(value)
            elif action == ActionTypes.SELECT_RADIO:
                target.Select()
            else:
                raise ValueError(f"Unknown field action: {action}")
            
            # --- VERIFIED WRITE BLOCK ---
            verification = self._verify_value(target, value)
            warnings = []
            
            if not verification["success"] and action != ActionTypes.SELECT_RADIO:
                warnings.append(
                    f"Field was set to '{value}' but reads back as '{verification['actual']}'. "
                    "This may be due to SAP formatting or a silent failure."
                )

            return ActionResult(
                success=True,
                action_type=action,
                target_id=request.target_id,
                message="Field updated successfully",
                completed_action_details={
                    "old_value": old_value, 
                    "requested_value": value,
                    "actual_value": verification["actual"],
                    "verification_outcome": verification["outcome"]
                },
                warnings=warnings
            )
        except Exception as e:
            logger.error(f"Failed field action {request.action_type} on {target_id}: {str(e)}")
            return ActionResult(
                success=False,
                action_type=request.action_type,
                target_id=request.target_id,
                error=str(e)
            )

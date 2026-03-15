from typing import Any
from ...schemas import ActionRequest, ActionResult
from .base_handler import ActionHandler
from loguru import logger

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
            
            old_value = None
            if hasattr(target, "Text"):
                old_value = target.Text
            elif hasattr(target, "Key"):
                old_value = target.Key
                
            if request.action_type in ("set_field", "set_value"):
                if target.Type == "GuiComboBox":
                    target.Key = str(value)
                else:
                    target.Text = str(value)
            elif request.action_type == "set_checkbox":
                if hasattr(target, "Key"):
                    target.Key = value
                else:
                    target.Selected = bool(value)
            elif request.action_type == "select_radio":
                target.Select()
            else:
                raise ValueError(f"Unknown field action: {request.action_type}")
            
            # --- VERIFIED WRITE BLOCK ---
            # After interaction, read back the value to verify
            actual_new_value = None
            if hasattr(target, "Text"):
                actual_new_value = target.Text
            elif hasattr(target, "Key"):
                actual_new_value = target.Key
            elif hasattr(target, "Selected"):
                actual_new_value = target.Selected

            verification_outcome = "SUCCESS"
            warnings = []
            
            # Simple check for direct value equality
            # (Note: Some SAP fields might format values, e.g. "100" -> "100.00", 
            # so we use loose comparison or just log the diff)
            if str(actual_new_value).strip() != str(value).strip() and request.action_type != "select_radio":
                warnings.append(f"Field was set to '{value}' but reads back as '{actual_new_value}'. This may be due to SAP formatting or a silent failure.")
                verification_outcome = "MISMATCH"

            return ActionResult(
                success=True,
                action_type=request.action_type,
                target_id=request.target_id,
                message=f"Field updated successfully",
                completed_action_details={
                    "old_value": old_value, 
                    "requested_value": value,
                    "actual_value": actual_new_value,
                    "verification_outcome": verification_outcome
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

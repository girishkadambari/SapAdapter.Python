from typing import Any
from ...schemas import ActionRequest, ActionResult
from .base_handler import ActionHandler
from loguru import logger

class ShellHandler(ActionHandler):
    """
    Handles SAP GuiShell components including Tree, Toolbar, and Picture.
    Supports actions: `select_node`, `expand_node`, `double_click_node`, `press_button`
    """
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        target_id = self._normalize_target_id(request.target_id)
        params = request.params or {}
        action = request.action_type
        
        try:
            target = session.FindById(target_id)
            subtype = str(target.SubType)
            
            if subtype == "Tree":
                node_key = params.get("node_key")
                if action == "find_node_by_path":
                    path = params.get("path")
                    try:
                        key = target.FindNodeKeyByPath(path)
                        return ActionResult(success=True, action_type=action, target_id=target_id, message=f"Found: {key}", completed_action_details={"node_key": key})
                    except:
                        return ActionResult(success=False, action_type=action, target_id=target_id, error=f"Path '{path}' not found in tree.")
                
                if not node_key:
                    raise ValueError(f"node_key is required for Tree action {action}")

                if action == "select_node":
                    target.SelectNode(node_key)
                elif action == "expand_node":
                    target.ExpandNode(node_key)
                elif action == "collapse_node":
                    target.CollapseNode(node_key)
                elif action == "double_click_node":
                    target.DoubleClickNode(node_key)
                else:
                    raise ValueError(f"Unsupported Tree action: {action}")
                msg = f"Tree action {action} on {node_key}"

            elif subtype == "Toolbar":
                button_id = params.get("button_id")
                if action == "press_button":
                    target.PressButton(button_id)
                elif action == "press_context_button":
                    target.PressContextButton(button_id)
                elif action == "select_menu_item":
                    target.SelectMenuItem(button_id)
                else:
                    raise ValueError(f"Unsupported Toolbar action: {action}")
                msg = f"Toolbar action {action} on {button_id}"

            elif subtype == "GridView":
                # GridView is often a Shell, delegate to common logic if possible
                # But here we implement native GridView Shell methods
                row = int(params.get("row", 0))
                col = params.get("column")
                if action == "activate_cell":
                    target.DoubleClick(row, col)
                elif action == "select_row":
                    target.SelectedRows = str(row)
                else:
                    raise ValueError(f"Unsupported GridView Shell action: {action}")
                msg = f"GridView action {action} on row {row}"
                
            else:
                # Generic fallback for pictures etc
                if action == "click":
                    target.Click(int(params.get("x", 0)), int(params.get("y", 0)))
                    msg = "Clicked on shell"
                else:
                    raise ValueError(f"Unsupported Shell subtype {subtype} for action {action}")

            return ActionResult(success=True, action_type=action, target_id=target_id, message=msg)

        except Exception as e:
            logger.error(f"Shell action {action} failed: {str(e)}")
            return ActionResult(success=False, action_type=action, target_id=target_id, error=str(e))

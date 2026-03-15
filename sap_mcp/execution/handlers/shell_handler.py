from loguru import logger
from ...schemas import ActionRequest, ActionResult
from ...core.config import ActionTypes, ShellSubtypes
from .base_handler import ActionHandler
from typing import Any

class ShellHandler(ActionHandler):
    """
    Handles complex SAP GuiShell components (Tree, Toolbar, etc.).
    """
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        target_id = self._normalize_target_id(request.target_id)
        params = request.params or {}
        action = request.action_type
        
        try:
            target = session.FindById(target_id)
            subtype = str(target.SubType)
            
            if subtype == ShellSubtypes.TREE:
                return self._handle_tree(target, action, params)
            elif subtype == ShellSubtypes.TOOLBAR:
                return self._handle_toolbar(target, action, params)
            elif subtype == ShellSubtypes.GRID_VIEW:
                return self._handle_grid_shell(target, action, params)
            else:
                return self._handle_generic_shell(target, action, params)

        except Exception as e:
            logger.error(f"Shell action {action} failed: {str(e)}")
            return ActionResult(success=False, action_type=action, target_id=target_id, error=str(e))

    def _handle_tree(self, target, action, params) -> ActionResult:
        node_key = params.get("node_key")
        
        if action == ActionTypes.FIND_NODE_BY_PATH:
            path = params.get("path")
            key = target.FindNodeKeyByPath(path)
            return ActionResult(success=True, action_type=action, target_id=target.Id, message=f"Found: {key}", completed_action_details={"node_key": key})
        
        if not node_key:
            raise ValueError(f"node_key required for tree action {action}")

        if action == ActionTypes.SELECT_NODE: target.SelectNode(node_key)
        elif action == ActionTypes.EXPAND_NODE: target.ExpandNode(node_key)
        elif action == ActionTypes.COLLAPSE_NODE: target.CollapseNode(node_key)
        elif action == ActionTypes.DOUBLE_CLICK_NODE: target.DoubleClickNode(node_key)
        else: raise ValueError(f"Unknown tree action: {action}")
        
        return ActionResult(success=True, action_type=action, target_id=target.Id, message=f"Tree: {action} on {node_key}")

    def _handle_toolbar(self, target, action, params) -> ActionResult:
        btn = params.get("button_id")
        if action == ActionTypes.PRESS_BUTTON: target.PressButton(btn)
        elif action == ActionTypes.PRESS_CONTEXT_BUTTON: target.PressContextButton(btn)
        elif action == ActionTypes.SELECT_MENU_ITEM: target.SelectMenuItem(btn)
        else: raise ValueError(f"Unknown toolbar action: {action}")
        
        return ActionResult(success=True, action_type=action, target_id=target.Id, message=f"Toolbar: {action} on {btn}")

    def _handle_grid_shell(self, target, action, params) -> ActionResult:
        row = int(params.get("row", 0))
        col = params.get("column")
        if action == ActionTypes.ACTIVATE_CELL: target.DoubleClick(row, col)
        elif action == ActionTypes.SELECT_ROW: target.SelectedRows = str(row)
        else: raise ValueError(f"Unknown GridView shell action: {action}")
        
        return ActionResult(success=True, action_type=action, target_id=target.Id, message=f"GridShell: {action} on row {row}")

    def _handle_generic_shell(self, target, action, params) -> ActionResult:
        if action == ActionTypes.CLICK:
            target.Click(int(params.get("x", 0)), int(params.get("y", 0)))
            return ActionResult(success=True, action_type=action, target_id=target.Id, message="Clicked generic shell")
        raise ValueError(f"Unsupported shell action: {action} for subtype {getattr(target, 'SubType', 'Unknown')}")

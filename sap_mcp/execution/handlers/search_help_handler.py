from typing import Any
from .base_handler import ActionHandler
from ...schemas import ActionRequest, ActionResult

class SearchHelpHandler(ActionHandler):
    """
    Handler for semantic Search Help (F4) interactions.
    Handles selection from both modern Grids and legacy amodal lists.
    """
    
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        action = request.action_type
        
        if action == "interaction_search_help_select":
            return await self._select_entry(session, request)
        
        raise ValueError(f"Action {action} not supported by SearchHelpHandler")

    async def _select_entry(self, session: Any, request: ActionRequest) -> ActionResult:
        """
        Logic for selecting an entry from a search help hit-list.
        """
        row = request.params.get("row", 0)
        
        try:
            active_window = session.ActiveWindow
            if not active_window or active_window.Type != "GuiModalWindow":
                # Some search helps are amodal or merged into the main window (less common for hit lists)
                # But typically they are wnd[1]+
                pass

            # 1. Try to find a selection control (Grid or Table)
            table_control = self._find_list_control(active_window or session.ActiveWindow)
            
            if table_control:
                if table_control.Type == "GuiGridView":
                    # GridView usually requires a double-click or select + enter
                    # We'll try double click as it's the most common selection trigger
                    table_control.doubleClickRow(row)
                elif table_control.Type == "GuiTableControl":
                    table_control.getAbsoluteRow(row).selected = True
                    session.sendVKey(0) # Confirm
                
                return ActionResult(
                    success=True,
                    action_type=request.action_type,
                    message=f"Selected row {row} via technical control {table_control.Id}"
                )
            
            # 2. Fallback: Keyboard/Click selection for Legacy Lists
            # Many legacy hit lists are just text in a GuiUserArea.
            # We use arrow keys to navigate and Enter to confirm.
            
            # Ensure focus is on the window/area
            active_window.setFocus()
            
            # If row > 0, navigate down
            for _ in range(row):
                session.sendVKey(2) # Down Arrow
            
            # Send Enter to confirm selection
            session.sendVKey(0) # Enter
            
            return ActionResult(
                success=True,
                action_type=request.action_type,
                message=f"Selected row {row} via keyboard fallback (VKEYs)"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type=request.action_type,
                error=f"Search help selection failed: {str(e)}"
            )

    def _find_list_control(self, container: Any) -> Any:
        """Recursively find a GridView or TableControl."""
        if not container:
            return None
            
        if container.Type in ("GuiGridView", "GuiTableControl"):
            return container
            
        if hasattr(container, "Children"):
            for i in range(container.Children.Count):
                child = container.Children.Item(i)
                found = self._find_list_control(child)
                if found:
                    return found
        return None

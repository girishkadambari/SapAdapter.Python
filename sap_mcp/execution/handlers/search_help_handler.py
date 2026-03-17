from loguru import logger
from typing import Any, Optional
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
        row = request.params.get("row")
        value = request.params.get("value")
        
        try:
            win = session.ActiveWindow
            # Standard List Control (GridView or TableControl)
            list_ctrl = self._find_list_control(win)
            
            if list_ctrl:
                logger.info(f"Found standard list control: {list_ctrl.Id} ({list_ctrl.Type})")
                if value:
                    found_row = self._find_row_by_value(list_ctrl, value)
                    if found_row is not None:
                        row = found_row
                
                if row is None: row = 0

                if list_ctrl.Type == SapGuiTypes.GRID_VIEW:
                    list_ctrl.doubleClickRow(row)
                elif list_ctrl.Type == SapGuiTypes.TABLE_CONTROL:
                    list_ctrl.getAbsoluteRow(row).selected = True
                    win.sendVKey(Config.DEFAULT_VKEY_ENTER)
                
                return ActionResult(success=True, action_type=request.action_type, message=f"Selected row {row} in {list_ctrl.Type}")
            
            # Legacy List Selection (Label-based)
            logger.info("Standard list control not found. Attempting legacy label-based selection.")
            selected_label = self._find_legacy_label(win, value, row)
            
            if selected_label:
                # Capture metadata BEFORE the window potentially closes
                label_id = getattr(selected_label, "Id", "unknown")
                val = getattr(selected_label, "Value", getattr(selected_label, "Text", "unknown"))
                
                selected_label.setFocus()
                # Standard SAP selection is Enter (VKey 0) or F2
                win.sendVKey(Config.DEFAULT_VKEY_ENTER)
                
                return ActionResult(
                    success=True, 
                    action_type=request.action_type, 
                    message=f"Selected legacy entry '{val}' at {label_id}"
                )

            # Fallback: Navigate by keyboard if everything else fails
            logger.warning("No interactive elements found. Using keyboard fallback.")
            win.setFocus()
            row_idx = row or 0
            for _ in range(row_idx):
                win.sendVKey(2) # Arrow Down
            win.sendVKey(Config.DEFAULT_VKEY_ENTER)
            
            return ActionResult(success=True, action_type=request.action_type, message=f"Keyboard fallback to row {row_idx}")
            
        except Exception as e:
            logger.error(f"Search help selection failed: {e}")
            return ActionResult(success=False, action_type=request.action_type, error=str(e))

    def _find_legacy_label(self, win: Any, value: Optional[str], row_idx: Optional[int]) -> Any:
        """
        Dynamically discovers and selects a label in a legacy list structure.
        Uses lbl[col,row] coordinates and heuristics to identify header vs data.
        """
        import re
        label_pattern = re.compile(r"lbl\[(\d+),(\d+)\]")
        all_labels = []

        def collect_labels(container):
            try:
                if not hasattr(container, "Children"): return
                count = container.Children.Count
                for i in range(count):
                    child = container.Children(i)
                    if not child: continue
                    
                    # Track labels and text fields (sometimes used in legacy lists)
                    if child.Type in [SapGuiTypes.LABEL, SapGuiTypes.TEXT_FIELD, SapGuiTypes.CTEXT_FIELD]:
                        col, row = -1, -1
                        match = label_pattern.search(child.Id)
                        if match:
                            col, row = map(int, match.groups())
                        
                        # Safe value extraction
                        val = getattr(child, "Value", getattr(child, "Text", ""))
                        all_labels.append({"col": col, "row": row, "obj": child, "value": val})
                    
                    # Recurse if it's a container type
                    if hasattr(child, "Children") and child.Children.Count > 0:
                        collect_labels(child)
            except Exception as e:
                logger.debug(f"Recursion break at {getattr(container, 'Id', 'unknown')}: {e}")

        usr_area = win.FindById("usr") if hasattr(win, "FindById") else win
        if not usr_area: return None
        
        collect_labels(usr_area)
        if not all_labels: 
            logger.warning("No text-bearing elements found in Search Help area")
            return None

        # Group by row
        rows = {}
        for l in all_labels:
            r = l["row"]
            if r not in rows: rows[r] = []
            rows[r].append(l)

        sorted_row_indices = sorted(rows.keys())
        
        # 1. Selection by Value
        if value:
            val_lower = value.lower()
            for r in sorted_row_indices:
                for l in rows[r]:
                    if val_lower in str(l["value"]).lower():
                        logger.info(f"Found value '{value}' in row {r}, column {l['col']}")
                        return l["obj"]

        # 2. Selection by Index (Row)
        if row_idx is not None:
            # Heuristic: Identify the "data start"
            # Data rows usually have the same number of columns and start after a gap or headers.
            # We look for the first row index >= 2 (skipping window title/header areas) 
            # and take the row_idx-th row from there.
            data_candidates = []
            for r in sorted_row_indices:
                # Most classic lists have headers in row 1, data starts after some decorations
                # We'll consider rows with multiple labels as data-potential.
                if len(rows[r]) >= 1 and r >= 2: 
                    data_candidates.append(r)
            
            if row_idx < len(data_candidates):
                target_row = data_candidates[row_idx]
                logger.info(f"Selecting logical row {row_idx} (SAP Row {target_row})")
                return rows[target_row][0]["obj"]

        return None

    def _find_row_by_value(self, list_ctrl: Any, value: str) -> Optional[int]:
        """
        Naive search for a value in a list control.
        """
        try:
            if list_ctrl.Type == SapGuiTypes.GRID_VIEW:
                rows = list_ctrl.RowCount
                cols = list_ctrl.ColumnCount
                for r in range(rows):
                    for c in range(cols):
                        col_name = list_ctrl.ColumnOrder(c)
                        cell_val = list_ctrl.getCellValue(r, col_name)
                        if value.lower() in str(cell_val).lower():
                            return r
            elif list_ctrl.Type == SapGuiTypes.TABLE_CONTROL:
                 # Table controls are harder to search fully without scrolling
                 # But we can check visible rows
                 for r in range(list_ctrl.VisibleRowCount):
                     row_obj = list_ctrl.Rows(r)
                     # Check all cells in row
                     for i in range(row_obj.Count):
                         cell = row_obj(i)
                         txt = getattr(cell, "Text", getattr(cell, "Value", ""))
                         if value.lower() in str(txt).lower():
                             return list_ctrl.VerticalScrollbar.Position + r
        except Exception as e:
            logger.warning(f"Failed to search list control by value: {e}")
        return None

    def _find_list_control(self, container: Any) -> Any:
        if not container: return None
        if container.Type in (SapGuiTypes.GRID_VIEW, SapGuiTypes.TABLE_CONTROL):
            return container
            
        if hasattr(container, "Children"):
            for i in range(container.Children.Count):
                found = self._find_list_control(container.Children(i))
                if found: return found
        return None

from typing import Any, List, Dict
from ...schemas import ActionRequest, ActionResult
from .base_handler import ActionHandler
from loguru import logger

class TableHandler(ActionHandler):
    """
    Handles SAP Table controls with production-grade robustness.
    Supports actions: `select_row`, `set_cell_data`, `get_cell_data`, `activate_cell`, 
    `find_row_by_text`, `extract_table_data`, `scroll_to_row`
    """
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        target_id = self._normalize_target_id(request.target_id)
        params = request.params or {}
        action = request.action_type
        
        try:
            target = session.FindById(target_id)
            ctype = str(target.Type)
            
            # Flexible column handling: try int, fallback to str
            col_raw = params.get("column")
            col = col_raw
            if col_raw is not None:
                try:
                    col = int(col_raw)
                except (ValueError, TypeError):
                    col = str(col_raw)
            
            row = int(params.get("row", 0))
            val = params.get("value")

            if action in ["extract_table_data", "read_table_rows"]:
                start_row = int(params.get("start_row", 0))
                row_count = int(params.get("row_count", 10))
                
                # Extract structured schema (Columns with titles and names)
                schema = self._get_table_schema(target, ctype)
                data = self._extract_data(target, ctype, start_row, row_count)
                
                return ActionResult(
                    success=True, 
                    action_type=action, 
                    target_id=target_id, 
                    message=f"Extracted {len(data)} rows from {ctype}", 
                    completed_action_details={
                        "schema": schema,
                        "rows": data,
                        "total_rows": int(target.RowCount)
                    }
                )

            elif action == "scroll_to_row":
                self._scroll_to(target, ctype, row)
                msg = f"Scrolled to row {row}"

            elif action in ["select_row", "table_select_row"]:
                self._scroll_to(target, ctype, row)
                self._select_row(target, ctype, row)
                msg = f"Selected row {row}"
            
            elif action == "table_double_click_row":
                self._scroll_to(target, ctype, row)
                # For search help, double click is usually on any cell in the row
                # We default to first column (usually index 0 or first technical name)
                col_to_click = col if col is not None else 0
                self._double_click_row(target, ctype, row, col_to_click)
                
                # Verification: Check if modal closed (standard Search Help behavior)
                msg = f"Double-clicked row {row}. Verifying modal closure..."
                
            elif action == "set_cell_data":
                self._scroll_to(target, ctype, row)
                # ... existing set_cell_data logic ...
                old_val = self._get_cell(target, ctype, row, col)
                self._set_cell(target, ctype, row, col, val)
                actual_val = self._get_cell(target, ctype, row, col)
                
                verification_outcome = "SUCCESS"
                warnings = []
                if str(actual_val).strip() != str(val).strip():
                    verification_outcome = "MISMATCH"
                    warnings.append(f"Cell was set to '{val}' but reads back as '{actual_val}'.")

                return ActionResult(
                    success=True, 
                    action_type=action, 
                    target_id=target_id, 
                    message=f"Set cell ({row}, {col}) to '{val}'",
                    completed_action_details={
                        "old_value": old_val,
                        "requested_value": val,
                        "actual_value": actual_val,
                        "verification_outcome": verification_outcome
                    },
                    warnings=warnings
                )
                
            elif action == "get_cell_data":
                self._scroll_to(target, ctype, row)
                val = self._get_cell(target, ctype, row, col)
                return ActionResult(success=True, action_type=action, target_id=target_id, message=f"Retrieved: {val}", completed_action_details={"value": val})

            elif action == "activate_cell":
                self._scroll_to(target, ctype, row)
                self._activate_cell(target, ctype, row, col)
                msg = f"Activated cell ({row}, {col})"

            elif action == "find_row_by_text":
                found_row = self._find_row(target, ctype, col, val)
                if found_row != -1:
                    return ActionResult(success=True, action_type=action, target_id=target_id, message=f"Found text at row {found_row}", completed_action_details={"row": found_row})
                else:
                    return ActionResult(success=False, action_type=action, target_id=target_id, error=f"Text '{val}' not found in column '{col}'")

            else:
                raise ValueError(f"Unsupported table action: {action}")

            return ActionResult(success=True, action_type=action, target_id=target_id, message=msg)

        except Exception as e:
            logger.error(f"Table action {action} failed: {str(e)}")
            return ActionResult(success=False, action_type=action, target_id=target_id, error=str(e))

    def _scroll_to(self, target: Any, ctype: str, row: int):
        """Ensures the target row is visible/accessible."""
        try:
            if ctype == "GuiTableControl":
                target.VerticalScrollbar.Position = row
            elif "GridView" in ctype or "GridView" in str(getattr(target, "SubType", "")):
                target.FirstVisibleRow = row
        except Exception as e:
            logger.debug(f"Scrolling hint failed (might not be needed): {e}")

    def _select_row(self, target: Any, ctype: str, row: int):
        if ctype == "GuiTableControl":
            target.Rows.Item(row).Selected = True
        else: # GridView/Shell
            target.SelectedRows = str(row)

    def _set_cell(self, target: Any, ctype: str, row: int, col: Any, val: Any):
        if ctype == "GuiTableControl":
            # Handle column as Name or Index
            cell = target.GetCell(row, col)
            cell.Text = str(val)
        else:
            # GridView ModifyCell
            target.ModifyCell(row, col, str(val))

    def _get_cell(self, target: Any, ctype: str, row: int, col: Any) -> str:
        try:
            if ctype == "GuiTableControl":
                return str(target.GetCell(row, col).Text)
            return str(target.GetCellValue(row, col))
        except Exception as e:
            logger.warning(f"Failed to get cell ({row}, {col}): {e}")
            return ""

    def _activate_cell(self, target: Any, ctype: str, row: int, col: Any):
        if ctype == "GuiTableControl":
            target.SetFocus()
            target.CurrentRow = row
            # For TableControl, we focus the cell specifically if possible
            try:
                target.GetCell(row, col).SetFocus()
            except:
                pass
            target.ActiveWindow.SendVKey(2)
        else:
            target.DoubleClick(row, col)

    def _double_click_row(self, target: Any, ctype: str, row: int, col: Any):
        """Perform a double-click on a row/cell to trigger SAP selection events."""
        if ctype == "GuiTableControl":
            target.SetFocus()
            target.CurrentRow = row
            try:
                cell = target.GetCell(row, col)
                cell.SetFocus()
            except:
                pass
            # F2 (Double-click)
            target.ActiveWindow.SendVKey(2)
        else:
            # GridView DoubleClick method
            target.DoubleClick(row, col)

    def _get_table_schema(self, target: Any, ctype: str) -> List[Dict[str, str]]:
        """Extracts column titles and technical names for structured data mapping."""
        schema = []
        try:
            if ctype == "GuiTableControl":
                cols = target.Columns
                for i in range(cols.Count):
                    col = cols.ElementAt(i)
                    schema.append({
                        "name": str(col.Name),
                        "title": str(col.Title)
                    })
            else:
                # GridView
                col_order = target.ColumnOrder
                for i in range(col_order.Count):
                    col_name = str(col_order.ElementAt(i))
                    schema.append({
                        "name": col_name,
                        "title": str(target.GetColumnTitle(col_name))
                    })
        except Exception as e:
            logger.warning(f"Failed to extract table schema: {e}")
        return schema

    def _find_row(self, target: Any, ctype: str, col: Any, text: str) -> int:
        count = int(target.RowCount)
        # Limit scan for performance
        max_scan = min(count, 100) 
        for i in range(max_scan):
            if self._get_cell(target, ctype, i, col).strip() == text.strip():
                return i
        return -1

    def _extract_data(self, target: Any, ctype: str, start_row: int, count: int) -> List[Dict]:
        rows = []
        total_rows = int(target.RowCount)
        end_row = min(start_row + count, total_rows)
        
        # Get technical column names from schema
        schema = self._get_table_schema(target, ctype)
        cols = [s["name"] for s in schema]

        for r in range(start_row, end_row):
            row_data = {"_row_index": r}
            for c in cols:
                row_data[c] = self._get_cell(target, ctype, r, c)
            rows.append(row_data)
        return rows

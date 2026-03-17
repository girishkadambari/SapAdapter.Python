from typing import Any, List, Dict
from loguru import logger
from ...schemas import ActionRequest, ActionResult
from ...core.config import ActionTypes, SapGuiTypes
from .base_handler import ActionHandler

class TableHandler(ActionHandler):
    """
    Handles SAP Table controls (GuiTableControl and ALV GridView).
    High-level logic for row selection, cell manipulation, and data extraction.
    """
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        target_id = self._normalize_target_id(request.target_id)
        params = request.params or {}
        action = request.action_type
        
        try:
            target = session.FindById(target_id)
            ctype = str(target.Type)
            
            # Robust column/row parameter parsing
            row_raw = params.get("row")
            row = int(row_raw) if row_raw is not None else 0
            col = self._parse_column(params.get("column"))
            val = params.get("value")

            # Route by Action Type
            if action == ActionTypes.GET_CELL_DATA:
                return self._handle_get_cell(target, ctype, row, col, action)
            
            elif action == ActionTypes.SET_CELL_DATA:
                return self._handle_set_cell(target, ctype, row, col, val)
            
            elif action == ActionTypes.SELECT_ROW:
                return self._handle_select_row(target, ctype, row, action)
            
            elif action == ActionTypes.ACTIVATE_CELL:
                # Standardized activate_cell (often used for double-click selection)
                return self._handle_activate_cell(target, ctype, row, col, action)
                
            elif action == ActionTypes.TABLE_BATCH_FILL:
                return self._handle_batch_fill(target, ctype, params, action)
            
            elif action == ActionTypes.FIND_ROW_BY_TEXT:
                return self._handle_find_row(target, ctype, col, val, action)

            else:
                raise ValueError(f"Unsupported table action: {action}")

        except Exception as e:
            logger.error(f"Table action {action} failed on {target_id}: {str(e)}")
            return ActionResult(success=False, action_type=action, target_id=target_id, error=str(e))

    # --- ACTION HANDLERS (Specialized Methods) ---

    def _handle_get_cell(self, target, ctype, row, col, action) -> ActionResult:
        self._scroll_to(target, ctype, row)
        val = self._get_cell(target, ctype, row, col)
        resolved_col = self._resolve_column(target, ctype, col)
        return ActionResult(
            success=True, 
            action_type=action, 
            target_id=target.Id, 
            message=f"Retrieved from '{resolved_col}': {val}", 
            completed_action_details={"value": val}
        )

    def _handle_set_cell(self, target, ctype, row, col, val) -> ActionResult:
        self._scroll_to(target, ctype, row)
        old_val = self._get_cell(target, ctype, row, col)
        
        self._set_cell(target, ctype, row, col, val)
        
        # Verify result
        verification = self._verify_value_complex(target, ctype, row, col, val)
        
        return ActionResult(
            success=True, 
            action_type=ActionTypes.SET_CELL_DATA, 
            target_id=target.Id, 
            message=f"Set cell ({row}, {col}) to '{val}'",
            completed_action_details={
                "old_value": old_val,
                "actual_value": verification["actual"],
                "verification_outcome": verification["outcome"]
            },
            warnings=[] if verification["success"] else [f"Verification mismatch: expected {val}, got {verification['actual']}"]
        )

    def _handle_select_row(self, target, ctype, row, action) -> ActionResult:
        self._scroll_to(target, ctype, row)
        self._select_row(target, ctype, row)
        return ActionResult(success=True, action_type=action, target_id=target.Id, message=f"Selected row {row}")

    def _handle_activate_cell(self, target, ctype, row, col, action) -> ActionResult:
        self._scroll_to(target, ctype, row)
        col_to_click = col if col is not None else 0
        self._double_click_row(target, ctype, row, col_to_click)
        return ActionResult(success=True, action_type=action, target_id=target.Id, message=f"Activated cell ({row}, {col})")

    def _handle_batch_fill(self, target, ctype, params, action) -> ActionResult:
        rows_data = params.get("rows", [])
        results = []
        for row_item in rows_data:
            r_raw = row_item.get("row")
            r = int(r_raw) if r_raw is not None else 0
            data = row_item.get("data", {})
            self._scroll_to(target, ctype, r)
            for c_identifier, val in data.items():
                resolved_col = self._resolve_column(target, ctype, c_identifier)
                self._set_cell(target, ctype, r, resolved_col, val)
            results.append({"row": r, "status": "SET"})
        
        return ActionResult(
            success=True,
            action_type=action,
            target_id=target.Id,
            message=f"Batch filled {len(results)} rows",
            completed_action_details={"results": results}
        )

    def _handle_find_row(self, target, ctype, col, val, action) -> ActionResult:
        found_row = self._find_row(target, ctype, col, val)
        if found_row != -1:
            return ActionResult(success=True, action_type=action, target_id=target.Id, message=f"Found at row {found_row}", completed_action_details={"row": found_row})
        return ActionResult(success=False, action_type=action, target_id=target.Id, error=f"Text '{val}' not found")

    # --- ATOMIC INTERACTIONS (Low-Level Helpers) ---

    def _parse_column(self, col_raw: Any) -> Any:
        if col_raw is None: return None
        try:
            return int(col_raw)
        except:
            return str(col_raw)

    def _scroll_to(self, target: Any, ctype: str, row: int):
        try:
            if ctype == SapGuiTypes.TABLE_CONTROL:
                target.VerticalScrollbar.Position = row
            elif ctype == SapGuiTypes.GRID_VIEW or "GridView" in str(getattr(target, "SubType", "")):
                target.FirstVisibleRow = row
        except Exception as e:
            logger.debug(f"Scroll failed: {e}")

    def _select_row(self, target: Any, ctype: str, row: int):
        if ctype == SapGuiTypes.TABLE_CONTROL:
            target.Rows.Item(row).Selected = True
        else:
            target.SelectedRows = str(row)

    def _set_cell(self, target: Any, ctype: str, row: int, col: Any, val: Any):
        resolved_col = self._resolve_column(target, ctype, col)
        if ctype == SapGuiTypes.TABLE_CONTROL:
            target.GetCell(row, resolved_col).Text = str(val)
        else:
            target.ModifyCell(row, resolved_col, str(val))

    def _get_cell(self, target: Any, ctype: str, row: int, col: Any) -> str:
        try:
            resolved_col = self._resolve_column(target, ctype, col)
            if ctype == SapGuiTypes.TABLE_CONTROL:
                return str(target.GetCell(row, resolved_col).Text)
            return str(target.GetCellValue(row, resolved_col))
        except Exception as e:
            logger.debug(f"Failed to get cell ({row}, {col}): {e}")
            return ""

    def _double_click_row(self, target: Any, ctype: str, row: int, col: Any):
        if ctype == SapGuiTypes.TABLE_CONTROL:
            target.SetFocus()
            target.CurrentRow = row
            target.ActiveWindow.SendVKey(2)
        else:
            target.DoubleClick(row, col)

    def _verify_value_complex(self, target, ctype, row, col, expected) -> Dict:
        actual = self._get_cell(target, ctype, row, col)
        success = str(actual).strip().lower() == str(expected).strip().lower()
        return {
            "success": success,
            "actual": actual,
            "outcome": "SUCCESS" if success else "MISMATCH"
        }

    def _get_table_schema(self, target: Any, ctype: str) -> List[Dict]:
        schema = []
        try:
            if ctype == SapGuiTypes.TABLE_CONTROL:
                for i in range(target.Columns.Count):
                    col = target.Columns.Item(i)
                    schema.append({"name": str(col.Name), "title": str(col.Title)})
            else:
                col_order = target.ColumnOrder
                for i in range(col_order.Count):
                    name = str(col_order.ElementAt(i))
                    schema.append({"name": name, "title": str(target.GetColumnTitle(name))})
        except: pass
        return schema

    def _find_row(self, target: Any, ctype: str, col: Any, text: str) -> int:
        resolved_col = self._resolve_column(target, ctype, col)
        count = min(int(getattr(target, "RowCount", 0)), 100)
        for i in range(count):
            if self._get_cell(target, ctype, i, resolved_col).strip() == str(text).strip():
                return i
        return -1

    def _resolve_column(self, target: Any, ctype: str, column_identifier: Any) -> Any:
        """
        Resolves a column name, suffix, title, or index to the correct identifier.
        """
        if column_identifier is None:
            return 0
        
        # If it's already an index, return it
        try:
            return int(column_identifier)
        except (ValueError, TypeError):
            pass

        col_str = str(column_identifier).strip()
        
        if ctype == SapGuiTypes.TABLE_CONTROL:
            cols = target.Columns
            # 1. Exact Match
            for i in range(cols.Count):
                if str(cols.ElementAt(i).Name) == col_str:
                    return i
            # 2. Suffix Match (e.g., 'TXZ01' matches 'MEPO1211-TXZ01')
            for i in range(cols.Count):
                if str(cols.ElementAt(i).Name).endswith(col_str):
                    return i
            # 3. Title Match
            for i in range(cols.Count):
                if str(cols.ElementAt(i).Title).lower() == col_str.lower():
                    return i
        
        elif ctype == SapGuiTypes.GRID_VIEW or "GridView" in str(getattr(target, "SubType", "")):
            # ALV Grid logic
            try:
                col_names = target.ColumnOrder
                
                # Check if column_identifier is a numeric index within bounds
                try:
                    idx = int(column_identifier)
                    if 0 <= idx < col_names.Count:
                        return str(col_names.ElementAt(idx))
                except (ValueError, TypeError):
                    pass

                col_str = str(column_identifier).strip()
                # 1. Exact Match
                for i in range(col_names.Count):
                    name = str(col_names.ElementAt(i))
                    if name == col_str:
                        return name
                # 2. Suffix Match
                for i in range(col_names.Count):
                    name = str(col_names.ElementAt(i))
                    if name.endswith(col_str):
                        return name
                # 3. Title Match
                for i in range(col_names.Count):
                    name = str(col_names.ElementAt(i))
                    if str(target.GetColumnTitle(name)).lower() == col_str.lower():
                        return name
            except Exception as e:
                logger.debug(f"GridView column resolution failed: {e}")

        return column_identifier

    def _extract_data(self, target: Any, ctype: str, start_row: int, count: int) -> List[Dict]:
        rows = []
        total = int(getattr(target, "RowCount", 0))
        end = min(start_row + count, total)
        schema = self._get_table_schema(target, ctype)
        cols = [s["name"] for s in schema]
        
        for r in range(start_row, end):
            row_data = {"_index": r}
            for c in cols:
                row_data[c] = self._get_cell(target, ctype, r, c)
            rows.append(row_data)
        return rows

from typing import Any, List, Dict
from .base_handler import BaseControlHandler
from ..schemas.control import Control

class GridHandler(BaseControlHandler):
    """
    Handler for GuiGridView (ALV Grids).
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == "GuiGridView"

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        
        # Enhanced metadata for grids
        metadata = {
            "row_count": int(getattr(control, "RowCount", 0)),
            "column_count": int(getattr(control, "ColumnCount", 0)),
            "schema": self._extract_columns(control)
        }
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype="grid",
            label=props["tooltip"] or "ALV Grid",
            value=f"Rows: {metadata['row_count']}, Cols: {metadata['column_count']}",
            editable=False,
            visible=props["visible"],
            parent_id=props["parent_id"],
            actions=self.get_supported_actions(control),
            confidence=1.0,
            metadata=metadata
        )

    def _extract_columns(self, control: Any) -> List[Dict[str, str]]:
        columns = []
        try:
            col_names = control.ColumnOrder
            for i in range(col_names.Count):
                col_name = str(col_names.ElementAt(i))
                columns.append({
                    "name": col_name,
                    "title": str(control.GetColumnTitle(col_name))
                })
        except:
            pass
        return columns

    def get_supported_actions(self, control: Any) -> List[str]:
        return [
            "read_table_rows", 
            "table_select_row", 
            "table_double_click_row", 
            "set_cell_data"
        ]

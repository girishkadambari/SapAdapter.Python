from typing import Any, List, Dict
from .base_handler import BaseControlHandler
from ..schemas.control import Control

class TableHandler(BaseControlHandler):
    """
    Handler for GuiTableControl (Standard SAP Tables).
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == "GuiTableControl"

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        
        # Enhanced metadata for tables
        metadata = {
            "row_count": int(getattr(control, "RowCount", 0)),
            "visible_row_count": int(getattr(control, "VisibleRowCount", 0)),
            "columns": self._extract_columns(control)
        }
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype="table",
            label=props["tooltip"] or "SAP Table",
            value=f"Rows: {metadata['row_count']}, Visible: {metadata['visible_row_count']}",
            editable=False,
            visible=props["visible"],
            parent_id=props["parent_id"],
            actions=self.get_supported_actions(control),
            confidence=1.0
        )

    def _extract_columns(self, control: Any) -> List[Dict[str, str]]:
        columns = []
        try:
            cols = control.Columns
            for i in range(cols.Count):
                col = cols.ElementAt(i)
                columns.append({
                    "name": str(col.Name),
                    "title": str(col.Title)
                })
        except:
            pass
        return columns

    def get_supported_actions(self, control: Any) -> List[str]:
        return ["get_rows", "select_row", "scroll"]

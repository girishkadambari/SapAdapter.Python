from typing import Any, List, Dict
from typing import Any
from .base_extractor import BaseControlExtractor
from ...schemas.control import Control
from ...core.config import SapGuiTypes, ControlSubtypes

class TableExtractor(BaseControlExtractor):
    """
    Extractor for GuiTableControl (Standard SAP Tables).
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == SapGuiTypes.TABLE_CONTROL

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        
        # Extract rich metadata
        row_count = int(getattr(control, "RowCount", 0))
        visible_row_count = int(getattr(control, "VisibleRowCount", 0))
        columns = self._extract_columns(control)
        
        metadata = {
            "row_count": row_count,
            "visible_row_count": visible_row_count,
            "columns": columns
        }
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype=ControlSubtypes.TABLE,
            text=props["text"] or f"Table ({row_count} rows)",
            value=f"{row_count}",
            visible=props["visible"],
            editable=False,
            bounds=props.get("bounds"),
            parent_id=props["parent_id"],
            metadata=metadata
        )

    def _extract_columns(self, control: Any) -> List[Dict[str, str]]:
        columns = []
        try:
            cols = control.Columns
            for i in range(cols.Count):
                col = cols.ElementAt(i)
                columns.append({
                    "name": str(col.Name),
                    "title": str(col.Title),
                    "index": i
                })
        except:
            pass
        return columns

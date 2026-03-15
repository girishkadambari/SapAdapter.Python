from typing import Any, List, Dict
from typing import Any
from .base_extractor import BaseControlExtractor
from ...schemas.control import Control
from ...core.config import SapGuiTypes, ControlSubtypes

class GridExtractor(BaseControlExtractor):
    """
    Extractor for GuiGridView (ALV Grids).
    """
    
    def identify(self, control: Any) -> bool:
        return str(control.Type) == SapGuiTypes.GRID_VIEW

    def extract(self, control: Any) -> Control:
        props = self.get_basic_props(control)
        
        # Extract rich metadata
        row_count = int(getattr(control, "RowCount", 0))
        columns = self._extract_columns(control)
        
        metadata = {
            "row_count": row_count,
            "columns": columns
        }
        
        return Control(
            id=props["id"],
            type=props["type"],
            subtype=ControlSubtypes.GRID,
            text=props["text"] or f"Grid ({row_count} rows)",
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
            # For GridView, we use ColumnOrder or specific API
            # Note: This is a simplified version, real ALV can be complex
            col_names = control.ColumnOrder
            for i in range(col_names.Count):
                col_name = str(col_names.ElementAt(i))
                columns.append({
                    "name": col_name,
                    "title": str(control.GetColumnTitle(col_name)),
                    "index": i
                })
        except:
            # Fallback for shells that might not expose ColumnOrder directly
            pass
        return columns

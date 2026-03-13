from typing import Any, List, Dict
from ..runtime.sap_runtime import SapRuntime

class GridExtractor:
    """
    Service to extract data from GuiGridView (ALV).
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime

    async def extract_all_rows(self, session_id: str, grid_id: str) -> List[Dict[str, str]]:
        """
        Extracts all rows from an ALV grid using technical column names.
        """
        session = self.runtime.get_session(session_id)
        grid = session.FindById(grid_id)
        
        if str(grid.Type) != "GuiGridView":
            # Some grids are inside shells
            if str(grid.Type) == "GuiShell" and "grid" in str(getattr(grid, "SubType", "")).lower():
                pass
            else:
                raise ValueError(f"Control {grid_id} is not a GridView")
                
        rows = []
        row_count = int(grid.RowCount)
        col_names = grid.ColumnOrder
        
        # Note: Large grids should be extracted incrementally, but for MVP we take all
        for i in range(row_count):
            row_data = {}
            for j in range(col_names.Count):
                col_name = str(col_names.ElementAt(j))
                row_data[col_name] = str(grid.GetCellValue(i, col_name))
            rows.append(row_data)
            
        return rows

from typing import Any, List, Dict
from ..schemas.observation import ScreenObservation
from ..runtime.sap_runtime import SapRuntime

class TableExtractor:
    """
    Service to extract data from GuiTableControl.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime

    async def extract_visible_rows(self, session_id: str, table_id: str) -> List[Dict[str, str]]:
        """
        Extracts all currently visible rows from a standard SAP table.
        """
        session = self.runtime.get_session(session_id)
        table = session.FindById(table_id)
        
        if str(table.Type) != "GuiTableControl":
            raise ValueError(f"Control {table_id} is not a TableControl")
            
        rows = []
        visible_rows = int(table.VisibleRowCount)
        columns = table.Columns
        
        for i in range(visible_rows):
            row_data = {}
            for j in range(columns.Count):
                col = columns.ElementAt(j)
                try:
                    # In TableControl, cells are accessed via table.GetCell(row, col) 
                    # or more commonly by child path if they are text fields
                    cell = table.GetCell(i, j)
                    row_data[str(col.Title)] = str(cell.Text)
                except:
                    row_data[str(col.Title)] = ""
            
            # Skip empty rows (common at the end of tables)
            if any(row_data.values()):
                rows.append(row_data)
                
        return rows

# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/commands/handlers/grid.py
import re
from loguru import logger

def _evaluate_query(cell_val, op, target):
    if op == "EQ": return cell_val == target
    if op == "CONTAINS": return target in cell_val
    if op == "REGEX": return bool(re.search(target, cell_val, re.IGNORECASE))
    
    # Numeric ops
    try:
        def parse_num(v):
            cleaned = re.sub(r'[^\d.,-]', '', v).replace(',', '.')
            return float(cleaned)
        
        n1 = parse_num(cell_val)
        n2 = float(target)
        if op == "GT": return n1 > n2
        if op == "LT": return n1 < n2
    except:
        pass
    return False

async def get_grid_summary(session, payload):
    shell_id = payload.get("shellId")
    if not shell_id: raise ValueError("shellId required")
    
    logger.info(f"GRID_GET_SUMMARY: {shell_id}")
    grid = session.FindById(shell_id)
    
    row_count = int(grid.RowCount)
    col_count = int(grid.ColumnCount)
    columns = grid.ColumnOrder
    
    headers = {}
    for i in range(min(col_count, 30)):
        col_name = str(columns.Item(i))
        headers[col_name] = str(grid.GetColumnHeaderText(col_name))
        
    return {
        "rowCount": row_count,
        "colCount": col_count,
        "headers": headers
    }

async def get_grid_rows(session, payload):
    shell_id = payload.get("shellId")
    start_row = int(payload.get("startRow", 0))
    row_count_req = int(payload.get("rowCount", 10))
    
    if not shell_id: raise ValueError("shellId required")
    
    logger.info(f"GRID_GET_ROWS: {shell_id} [{start_row}..{start_row + row_count_req}]")
    grid = session.FindById(shell_id)
    
    col_order = payload.get("columns", [])
    if not col_order:
        cnt = int(grid.ColumnCount)
        order = grid.ColumnOrder
        for i in range(min(cnt, 20)):
            col_order.append(str(order.Item(i)))
            
    rows = []
    end_row = min(start_row + row_count_req, int(grid.RowCount), start_row + 50)
    
    for r in range(start_row, end_row):
        row_data = {}
        for col in col_order:
            row_data[col] = str(grid.GetCellValue(r, col))
        rows.append(row_data)
        
    return {"rows": rows}

async def find_grid_rows(session, payload):
    shell_id = payload.get("shellId")
    column = payload.get("column")
    op = payload.get("op", "EQ")
    value = str(payload.get("value", ""))
    limit = int(payload.get("limit", 10))
    
    if not shell_id or not column: raise ValueError("shellId and column required")
    
    logger.info(f"GRID_FIND_ROWS: {shell_id} ({column} {op} {value})")
    grid = session.FindById(shell_id)
    row_count = int(grid.RowCount)
    
    # Strategy: if column is not found in ColumnOrder, try matching by HeaderText
    col_id = column
    col_found = False
    order = grid.ColumnOrder
    col_cnt = int(grid.ColumnCount)
    
    for i in range(col_cnt):
        cid = str(order.Item(i))
        if cid == column:
            col_found = True
            break
        header = str(grid.GetColumnHeaderText(cid))
        if header == column:
            col_id = cid
            col_found = True
            break
            
    matches = []
    max_scan = min(row_count, 1000) # Safety limit
    max_matches = min(limit, 50)
    
    for r in range(max_scan):
        if len(matches) >= max_matches: break
        
        cell_val = str(grid.GetCellValue(r, col_id))
        if _evaluate_query(cell_val, op, value):
            matches.append({
                "rowIndex": r,
                "value": cell_val,
                "matchedCells": {col_id: cell_val},
                "matchReason": f"{op} match on column {col_id}"
            })
            
    return {"matches": matches}

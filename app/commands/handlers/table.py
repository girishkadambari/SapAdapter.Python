# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/commands/handlers/table.py
import re
from loguru import logger

def _evaluate_query(cell_val, op, target):
    if op == "EQ": return cell_val == target
    if op == "CONTAINS": return target in cell_val
    if op == "REGEX": return bool(re.search(target, cell_val, re.IGNORECASE))
    try:
        def parse_num(v):
            cleaned = re.sub(r'[^\d.,-]', '', v).replace(',', '.')
            return float(cleaned)
        n1 = parse_num(cell_val)
        n2 = float(target)
        if op == "GT": return n1 > n2
        if op == "LT": return n1 < n2
    except: pass
    return False

async def get_table_summary(session, payload):
    shell_id = payload.get("shellId")
    if not shell_id: raise ValueError("shellId required")
    
    logger.info(f"TABLE_GET_SUMMARY: {shell_id}")
    table = session.FindById(shell_id)
    
    row_count = int(table.RowCount)
    col_count = int(table.Columns.Count)
    
    headers = []
    for i in range(min(col_count, 20)):
        headers.append(str(table.Columns.Item(i).Name))
        
    return {
        "rowCount": row_count,
        "colCount": col_count,
        "headers": headers
    }

async def get_table_rows(session, payload):
    shell_id = payload.get("shellId")
    start_row = int(payload.get("startRow", 0))
    row_count_req = int(payload.get("rowCount", 10))
    
    if not shell_id: raise ValueError("shellId required")
    
    logger.info(f"TABLE_GET_ROWS: {shell_id} [{start_row}..{start_row + row_count_req}]")
    table = session.FindById(shell_id)
    col_count = int(table.Columns.Count)
    
    rows = []
    end_row = min(start_row + row_count_req, int(table.RowCount), start_row + 50)
    
    for r in range(start_row, end_row):
        row_data = {}
        for c in range(min(col_count, 20)):
            cell = table.GetCell(r, c)
            name = str(table.Columns.Item(c).Name)
            row_data[name] = str(cell.Text)
        rows.append(row_data)
        
    return {"rows": rows}

async def find_table_rows(session, payload):
    shell_id = payload.get("shellId")
    column = payload.get("column")
    op = payload.get("op", "EQ")
    value = str(payload.get("value", ""))
    limit = int(payload.get("limit", 10))
    
    if not shell_id or column is None: raise ValueError("shellId and column required")
    
    logger.info(f"TABLE_FIND_ROWS: {shell_id} ({column} {op} {value})")
    table = session.FindById(shell_id)
    row_count = int(table.RowCount)
    
    matches = []
    max_scan = min(row_count, 500)
    max_matches = min(limit, 50)
    
    for r in range(max_scan):
        if len(matches) >= max_matches: break
        
        try:
            # column could be index or name
            cell = table.GetCell(r, column)
            cell_val = str(cell.Text)
            
            if _evaluate_query(cell_val, op, value):
                matches.append({"rowIndex": r, "value": cell_val})
        except:
            continue
            
    return {"matches": matches}

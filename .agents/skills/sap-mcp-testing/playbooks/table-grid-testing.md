# Playbook: Table and Grid Testing

## Objective
Robust interaction with `GuiTableControl` (Classic Tables) and `GuiGridView` (ALV Grids).

## 1. Control Identification
Tables and Grids behave differently! 
- **Classic Table**: Has fixed rows in the summary. ID usually contains `tbl`.
- **ALV Grid**: Part of a `GuiShell`. ID usually contains `shellcont`.

## 2. Inspection
Before editing, call `sap_inspect_control` on the table ID:
- Get `RowCount`: How many total rows exist?
- Get `VisibleRowCount`: How many rows are currently on screen?
- Get `Columns`: What are the technical names (`MCHPF-CHARG`, etc.)?

## 3. Row and Cell Targeting
- **Indexing**: SAP logical rows start at 0.
- **Column Identity**: Use technical IDs (e.g., `MATNR`) rather than numeric indices if possible for stability.
- **Find Row**: If looking for a specific value, use `sap_table_action` with `find_row_by_text`.

## 4. Updates and Validation (`set_cell_data`)
1. Set the cell data.
2. **Crucial**: Send V-Key 0 (Enter) to commit the table change to the backend.
3. **Verify**: Use `get_cell_data` to read it back. If it's blank, the backend rejected the entry.

## 5. Safe Scrolling
- If target row index > `VisibleRowCount`, you must scroll.
- Use `sap_table_action` to activate the row; the MCP server should handle the auto-scroll via scripting. If it fails, report it as a `TABLE_GRID_FAILURE`.

## 6. Table Success Criteria
- `Value` matches input after Enter.
- Row remains selected if `select_row` was used.
- No error in Status Bar after cell entry.

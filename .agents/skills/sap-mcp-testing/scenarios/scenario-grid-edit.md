# Scenario: Generic Grid Edit

## Objective
Test interaction with modern `GuiGridView` (ALV) controls found in reports and dashboards.

## Flow
1. **Navigate**: `/nSE16N` (General Table Display).
2. **Table Selection**: 
   - Table: `MARA`
   - Maximum No. of Hits: `10`
   - Click "Online" (F8).
3. **Grid Interaction**:
   - Target Grid: `GuiShell` containing the ALV.
   - **Action**: Select a row and click "Details" or try to edit a cell (if in edit mode).
4. **Validation**:
   - Verify `sap_table_action` returns cell data correctly.
   - Test "Select All" / "Deselect All" toolbar buttons via `send_vkey` or `click`.

## Critical Verification Points
- Does the MCP server distinguish between the Toolbar and the Grid body?
- Can the agent read hidden columns by scrolling the grid horizontally?
- Does `find_row_by_text` work correctly on ALV columns?

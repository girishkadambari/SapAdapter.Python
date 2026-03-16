# Scenario: VA01 Sales Order Item Entry

## Objective
Test the full flow of creating a sales order item, including header data, item table interaction, and validation.

## Flow
1. **Navigate**: `/nVA01`
2. **Header Input**:
   - Order Type (`VBAK-AUART`): `OR`
   - Press Enter.
3. **Sales Area (if prompted)**:
   - Sales Org: `1010`
   - Distr. Channel: `10`
   - Division: `00`
   - Press Enter.
4. **Partner Data**:
   - Sold-To Party (`KUAGV-KUNNR`): `10100001`
   - Ship-To Party (`KUNWE-KUNNR`): `10100001`
   - PO Number: `TEST-AGV-01`
5. **Item Entry (The Table Test)**:
   - Target Table: `SAPMV45ATCTRL_U_ERF_AUFTRAG`
   - Row 0, Material Column: `TG11`
   - Row 0, Quantity Column: `10`
   - Press Enter.
6. **Validation**:
   - Check `StatusBar` for "Item 10 has been added" (or similar).
   - Use `sap_table_action(get_cell_data)` to verify "Net Value" is calculated (non-zero).
7. **Save**:
   - Send V-Key 11.
   - Verify `StatusBar` contains "Sales Order XXXXX has been saved".

## Critical Verification Points
- Does Enter move the focus to the next logical field?
- Does the table resize correctly after adding one item?
- Does `get_status_and_incompletion` show any missing pricing or shipping data?

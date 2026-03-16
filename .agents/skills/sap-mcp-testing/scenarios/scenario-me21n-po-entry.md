# Scenario: ME21N Purchase Order Entry

## Objective
Test grid-based header entry and table-based item entry in the modern PO transaction.

## Flow
1. **Navigate**: `/nME21N`
2. **Expand Header** (if collapsed): Target `Expand/Collapse` button.
3. **Header Input**:
   - Vendor (`ADDR3_DATA-NAME1` or Search Help): `10100001`
   - Org Data Tab:
     - Purchase Org: `1010`
     - Purchase Group: `001`
     - Company Code: `1010`
4. **Item Overview (The Table Test)**:
   - Target Table: `SAPLMEGUITCTRL_1211`
   - Row 0, Material: `TG11`
   - Row 0, PO Quantity: `100`
   - Row 0, Plant: `1010`
   - Press Enter.
5. **Validation**:
   - Use `get_status_and_incompletion` to check for "Check" errors.
   - Verify Item Details tabs (Conditions, Delivery) appear.
6. **Save**:
   - Click Save (V-Key 11).
   - Verify success message.

## Critical Verification Points
- **Grid Context**: Does the vendor search help return correctly to the header?
- **F4 Validation**: Use search help for "Plant" and verify selection.
- **Async Latency**: ME21N is heavy; wait for `get_screen_summary` to show "Ready" between steps.

# Scenario: Display Flow (Read-Only)

## Objective
Test the agent's ability to navigate through display transactions and extract data without modifications.

## Flow
1. **Navigate**: `/nMM03` (Material Display)
2. **Target Input**:
   - Material: `TG11`
   - Press Enter.
3. **View Selection Modals**:
   - Select "Basic Data 1" from the popup list.
   - Press Enter.
4. **Data Extraction**:
   - Extract "Description" and "Base Unit of Measure".
   - Use `sap_inspect_control` to verify these are `Changeable: False`.
5. **Tab Navigation**:
   - Use `select_tab` to move to "Plant Data/Storage 1".
   - Extract "Storage Bin" (if exists).

## Critical Verification Points
- Does the "View Selection" modal correctly detect as an `ActiveWindow`?
- Can the agent reliably select from the list within the modal?
- Does navigation between tabs refresh the `screen_summary` accurately?

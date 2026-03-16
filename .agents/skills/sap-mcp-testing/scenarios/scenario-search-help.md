# Scenario: Generic Search Help

## Objective
Verify the end-to-end reliability of the F4 selection flow.

## Flow
1. **Navigate**: `/nMM01` (Create Material).
2. **Field Trigger**:
   - Industry Sector: Click F4 icon.
3. **Hit List Detection**:
   - Verify a popup appears.
   - Identify the list of sectors (e.g., "Mechanical Engineering", "Chemical Industry").
4. **Selection**:
   - Use `sap_search_help_select(value='M')` for Mechanical Engineering.
5. **Post-Select Validation**:
   - Verify the popup closed.
   - Verify the "Industry Sector" field now contains `M`.

## Critical Verification Points
- Does the agent wait for the "Hit List" to populate?
- How does the agent handle a "No values found" message in the status bar?
- Is the transfer from F4 to source field instantaneous or does it require a refresh?

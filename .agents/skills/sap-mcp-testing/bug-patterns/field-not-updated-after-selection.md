# Bug Pattern: Field Not Updated After Selection

## Symptom
`sap_search_help_select` returns `SUCCESS`, but the source field is still empty or has the old value.

## Likely Root Causes
1. **Handover Logic Failure**: The MCP tool selected the row but didn't trigger the "Double Click" or "Select" event that closes the popup.
2. **Validation Block**: SAP backend rejected the selected value due to a cross-field dependency error.
3. **UI Refresh**: The screen hasn't updated its metadata in the summary.

## Diagnosis Steps
- Check if the F4 popup is still open.
- Run `sap_inspect_control` on the source field to see the `Value` property.
- Check Status Bar for "Value X is not valid for field Y".

## Recommended Fix in Test
- Always validate the source field **after** the selection step.
- If failure persists, try `set_field` manually with the known value to see if it's a "Select" vs "Entry" issue.

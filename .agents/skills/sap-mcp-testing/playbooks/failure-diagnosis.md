# Playbook: Failure Diagnosis

## Classification System

| Code | Description | Symptoms |
| :--- | :--- | :--- |
| `SCREEN_UNDERSTANDING_FAILURE` | Agent cannot map the current UI. | Target ID missing from summary; Screen title mismatch. |
| `CONTROL_IDENTIFICATION_FAILURE` | Target control exists but is not what was expected. | `inspect_control` shows different type or `Changeable: False`. |
| `FIELD_INTERACTION_FAILURE` | `set_field` or `set_checkbox` failed technically. | Tool returns error; Screen value remains unchanged. |
| `TABLE_GRID_FAILURE` | Failed to read/write to a table cell. | Row index out of bounds; Cell data not sticking after Enter. |
| `SEARCH_HELP_FAILURE` | F4 flow interrupted or invalid selection. | Popup not detected; Selection didn't update source field. |
| `NAVIGATION_FAILURE` | T-Code or V-Key didn't reach target screen. | Screen title hasn't changed; Error in Status Bar. |
| `VALIDATION_FAILURE` | Action succeeded technically but business logic failed. | Document didn't save; Incompletion log is non-empty. |

## Root Cause Analysis (RCA) Steps

1. **Visual Check**: Run `sap_capture_visual`. Does the screenshot show an error dialog not captured in the summary?
2. **Context Check**: Run `get_sap_context`. Is the session still active? Is the T-Code what you think it is?
3. **Property Check**: Run `sap_inspect_control`. Is the control disabled (`Enabled: False`)?
4. **Log Review**: Check the MCP server logs for "Scripting Error" or "COM Exception".

## Debugging Recommendations
- **If `FIELD_INTERACTION_FAILURE`**: Try sending V-Key 0 (Enter) BEFORE setting the field to clear previous state.
- **If `TABLE_GRID_FAILURE`**: Verify if the table requires a specific "Edit Mode" button to be clicked first.
- **If `SEARCH_HELP_FAILURE`**: Check if the hit list is actually a `GuiGridView` (ALV) which requires `sap_table_action` instead of simple list selection.

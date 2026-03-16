# Playbook: Screen Analysis

## Objective
Establish a reliable map of the current SAP screen before performing any action.

## 1. Initial Observation (`sap_get_screen_summary`)
- **Key Fields to Parse**: 
  - `Title`: Confirms the transaction context.
  - `StatusBar`: Checks for system messages (Error/Warning/Success).
  - `HighValueControls`: Identifies the primary fields, buttons, and tables.

## 2. Deep Inspection (`sap_inspect_control`)
Use this when:
- Interacting with a control for the first time in a session.
- The control is part of a `GuiTableControl` or `GuiGridView`.
- Summary data is insufficient (missing labels, tooltips).

**Verification Points**:
- `Type`: Ensure it matches expected (e.g., `GuiTextField` vs `GuiCTextField`).
- `Changeable`: If `False`, do not attempt `set_field`.
- `Id`: Verify the absolute path is what you intend to target.

## 3. Detecting Dynamic State
- **Modals**: Check if `ActiveWindow` summary indicates a popup (e.g., "Identification" or "Save changes?").
- **Busy State**: If tool returns a timeout or busy error, wait and retry `get_screen_summary`.

## 4. Mapping Hierarchies
- If a target field is not in the summary, check parent containers (Tabs, Frames).
- Use `select_tab` if the field is hidden within an inactive tab page.

## Reporting Criteria
- **Inconsistent ID**: If the ID found via search doesn't match the summary ID.
- **Hidden Target**: If the field exists in the DOM but its bounds are 0 or it's not visible.

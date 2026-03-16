# Playbook: Safe Field Interaction

## Objective
Set field values reliably and verify the update was accepted by the SAP application logic.

## 1. Field Preparation
- **Identify**: Locate the ID via `sap_get_screen_summary`.
- **Confirm**: Use `sap_inspect_control` to verify:
  - `Changeable == True`
  - `FieldType` (is it a dropdown? use `set_field` with key).

## 2. Action (`set_field`)
- Send the value using the exact ID.
- For `GuiComboBox`, ensure the value passed is the **Key**, not the display text.

## 3. Semantic Validation
Technical success (`tool result: ok`) is insufficient.
**Perform one of the following**:
- **Immediate Re-read**: Run `sap_get_screen_summary` and check the `Value` attribute of that ID.
- **Trigger Round-trip**: Send V-Key 0 (Enter) and re-check. SAP often validates or formats fields after Enter.
- **Side-Effect Check**: Check if setting this field enabled/disabled other fields (e.g., setting "Sales Org" might enable "Distribution Channel").

## 4. Checkbox and Radio Buttons
- Use `set_checkbox` with `"True"` or `"False"`.
- For Radio Buttons, they are often grouped; setting one to `"True"` automatically sets others to `"False"`. Verify the whole group state.

## 5. Interaction Failure Modes
- **Read-Only**: Target is a label or display-only field.
- **Output-Only**: Field is for system messages.
- **Input Error**: Status bar says "Entry not allowed".

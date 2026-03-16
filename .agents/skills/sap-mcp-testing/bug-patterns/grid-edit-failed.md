# Bug Pattern: Grid Edit Failed

## Symptom
`sap_table_action(set_cell_data)` returns `OK`, but the value disappears after Enter or Save.

## Likely Root Causes
1. **Read-Only Mode**: The ALV Grid is in "Display" mode. Needs a "Change" button click.
2. **Input Validation**: The backend rejected the value (e.g., lowercase instead of uppercase).
3. **Format Mismatch**: Passing `10.00` to a field expecting `10,00` (Locale issue).

## Diagnosis Steps
- Check the `StatusBar` immediately after the action.
- Use `get_cell_data` to verify if the value is still there after the round-trip.
- Check if the field is `Changeable` in `inspect_control`.

## Recommended Fix in Test
- Always send V-Key 0 (Enter) after grid edits to force a backend sync.
- Normalize input data to SAP technical formats (Trim spaces, Uppercase).

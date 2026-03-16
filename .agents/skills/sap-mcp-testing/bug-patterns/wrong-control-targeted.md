# Bug Pattern: Wrong Control Targeted

## Symptom
The tool reports `SUCCESS`, but the user sees no change on screen, or a different field was updated.

## Likely Root Causes
1. **Index Shifting**: In `GuiTableControl`, logical indices shift if rows are deleted/inserted.
2. **ID Ambiguity**: Multiple fields have similar IDs, and the agent picked the wrong one from the summary.
3. **Dynamic IDs**: Some SAP custom fields change parts of their ID string per session.

## Diagnosis Steps
- Run `sap_inspect_control` on the ID you *thought* was correct. Check its `Text` or `Tooltip`.
- Run `sap_capture_visual` and compare the coordinates of the interaction to the visual layout.
- Compare IDs after a screen refresh (`sap_get_screen_summary`).

## Recommended Fix in Test
- Use absolute IDs from `inspect_control` instead of relative or short IDs.
- Validate the field's Label/Tooltip before interaction.

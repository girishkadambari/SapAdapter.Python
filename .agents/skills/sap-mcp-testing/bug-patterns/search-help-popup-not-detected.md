# Bug Pattern: Search Help Popup Not Detected

## Symptom
The agent triggers F4, but the next `get_screen_summary` still shows the main window, and `sap_search_help_select` fails.

## Likely Root Causes
1. **Network Latency**: The popup took 2 seconds to appear, but the agent checked at 0.5s.
2. **Dialog vs Shell**: The search help is embedded in a `GuiShell` rather than a new `GuiModalWindow`.
3. **Scripting Blocked**: SAP scripting is busy or blocked by a system dialog.

## Diagnosis Steps
- Add a manual retry/wait loop for the `ActiveWindow` title change.
- Run `sap_capture_visual` to see if the popup is visible but not in the object tree.
- Check `get_sap_context` for `WaitState`.

## Recommended Fix in Test
- Use a robust "wait for window" utility.
- Verify the `ChildrenCount` of the session increased by 1.

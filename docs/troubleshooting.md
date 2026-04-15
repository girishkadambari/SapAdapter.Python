# Troubleshooting Guide

This guide covers common issues encountered while setting up or running the SAP MCP Adapter.

## 1. Connection Failures

### `ValueError: Session not found`
- **Cause**: The session ID passed to the tool does not match any active sessions.
- **Solution**: Call `sap_list_sessions` again to refresh IDs. SAP sessions can expire or be closed by the user.

### `pythoncom` error (CoInitialize)
- **Cause**: Accessing COM objects from the wrong thread without initializing the COM library.
- **Solution**: The adapter uses a `ComExecutor` to handle this. If you are extending the code, ensure you use `executor.execute(func)` for any direct SAP COM calls.

## 2. SAP GUI Scripting Issues

### "Scripting not enabled for this system"
- **Cause**: The SAP server has `sapgui/user_scripting` set to `FALSE`.
- **Solution**: Contact your Basis administrator to change the parameter in `RZ11`.

### "No active session found"
- **Cause**: No SAP GUI window is open, or it is currently at the login screen where scripting might be limited.
- **Solution**: Ensure you are logged into a system and a window is active.

## 3. Tool Execution Failures

### `ActionDispatcher` Timeout
- **Cause**: SAP is too slow, or a modal dialog is blocking execution.
- **Solution**: Increase the `WaitStrategy` timeout in `Config` or check if there is an unhandled popup on the screen.

### "Control not found"
- **Cause**: The control ID has changed (common in dynamic tables) or the screen has navigated away.
- **Solution**: Always call `sap_observe_screen` before attempting an action to get the most recent valid IDs.

## 4. MCP Integration Issues

### Claude Desktop doesn't see tools
- **Cause**: The `claude_desktop_config.json` path is incorrect or Python dependencies are missing in the specified venv.
- **Solution**: Check the Claude logs (`%APPDATA%/Claude/logs/mcp.log`) for specific startup errors.

### "EOF Error" in Stdio
- **Cause**: The server crashed during startup. 
- **Solution**: Run `python mcp_stdio.py` manually in a terminal to see the traceback.

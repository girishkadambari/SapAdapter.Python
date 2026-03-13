# Windows VM Environment Checklist: SAP MCP Server

This checklist ensures the Windows VM is correctly configured for the SAP MCP server to operate reliably.

## 1. SAP GUI Installation & Configuration
- [ ] **SAP GUI Installed:** SAP GUI for Windows (7.70 or 8.00 recommended) is installed.
- [ ] **SAP Logon Pad:** SAP Logon Pad is configured with at least one active connection.
- [ ] **Scripting Enabled (Server-side):** The SAP system profile parameter `sapgui/user_scripting` is set to `TRUE`.
- [ ] **Scripting Enabled (Client-side):**
    - [ ] Open SAP GUI Options > Accessibility & Scripting > Scripting.
    - [ ] "Enable scripting" is CHECKED.
    - [ ] "Notify when a script attaches to SAP GUI" is UNCHECKED (for automated agents).
    - [ ] "Notify when a script opens a connection" is UNCHECKED.

## 2. Windows Environment
- [ ] **User Context:** SAP GUI and the MCP server process MUST run under the same Windows user account.
- [ ] **Screen Resolution:** Recommended 1920x1080 for stable screenshot capture and control identification.
- [ ] **Scaling:** Windows Display Scaling should be set to 100% to ensure coordinate mapping accuracy.

## 3. Python Environment
- [ ] **Python Version:** Python 3.10+ installed.
- [ ] **Virtual Environment:** `venv` created and activated.
- [ ] **Dependencies:** Run `pip install -r requirements.txt`.
    - [ ] `pywin32` (for COM interaction)
    - [ ] `pythoncom` (part of pywin32)
    - [ ] `pydantic` (for schemas)
    - [ ] `fastapi` / `mcp` (for server protocol)
    - [ ] `loguru` (for logging)

## 4. Connectivity & Startup
- [ ] **SAP Active:** At least one SAP session is logged in and sitting at the Easy Access menu or a transaction.
- [ ] **Mcp Server:** Run `python main.py`.
- [ ] **Ports:** Port 8787 (default) is open and not blocked by Windows Firewall.

## 5. Verification Command
Run the following check to verify COM connectivity:
```powershell
python -c "import win32com.client; sap = win32com.client.GetObject('SAPGUI'); app = sap.GetScriptingEngine; print(f'Sessions: {len(app.Children[0].Children)}')"
```
If this prints a session count, the environment is READY.

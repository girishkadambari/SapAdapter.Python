# Postman Usage Guide

This guide explains how to set up and run the SAP MCP Postman collection.

## 1. Prerequisites
- Windows VM with SAP GUI for Windows.
- Python 3.9+ environment with `sap_mcp` dependencies installed.
- Postman Desktop or Web.

## 2. Start the Test Adapter
Since Postman interacts best with HTTP, we use a separate test adapter that bridges HTTP to the SAP MCP logic.

1. Open a terminal in the project root.
2. Run the test adapter:
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   python tests/postman_adapter.py
   ```
   *Note: On Windows, use `set PYTHONPATH=%PYTHONPATH%;.`*

3. The bridge will start on `http://localhost:8788`.

## 3. Import Postman Assets
1. In Postman, click **Import**.
2. Select the files from the `postman/` directory:
   - `SAP_MCP_Local.postman_collection.json`
   - `SAP_MCP_Local.postman_environment.json`

## 4. Configure Environment
1. Select the **SAP MCP Local** environment in Postman.
2. Update variables if needed:
   - `base_url`: `http://localhost:8788`
   - `session_id`: (Will be populated by `list_sessions`).

## 5. Running Tests
The collection is organized numerically. Start with **01 Session Management** to discover your session, then proceed to **02 Observation**.

### Standard Workflow:
1. Run `list_sessions` -> It will automatically save the first `sessionId` to your environment.
2. Run `observe_screen` -> Verify the `screen_type` in the response.
3. Run `execute_action` -> Provide a `target_id` from the observation and check the `ActionResult`.

## 6. Troubleshooting
- **SAP Busy**: If the request hangs, SAP might be displaying a modal or processing a long request. The server has a 30s timeout.
- **Port Conflict**: If 8788 is taken, change it in `tests/postman_adapter.py` and the Postman environment.

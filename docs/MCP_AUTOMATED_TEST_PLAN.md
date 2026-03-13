# MCP Automated Validation Plan

This document outlines automated test cases that can be executed via Antigravity or a test runner to verify MCP tool determinism and stability.

## Test 1: Session Discovery (Stability)
- **Objective:** Verify `list_sessions` returns consistent data without COM exceptions.
- **Tool Call:**
  ```json
  { "name": "list_sessions", "arguments": {} }
  ```
- **Validation Logic:**
  - Response contains a list of strings or objects.
  - Length of list matches the number of open SAP windows.
- **Expected Outcome:** 100% success rate over 10 consecutive calls.

## Test 2: Observation Accuracy (Integrity)
- **Objective:** Ensure `observe_screen` captures nested controls.
- **Tool Call:**
  ```json
  { "name": "observe_screen", "arguments": { "include_screenshot": true } }
  ```
- **Validation Logic:**
  - `controls` list is not empty.
  - `screenshot_data` is present and valid base64.
  - `transaction` correctly reflects the active SAP transaction (e.g., "S000").
- **Expected Outcome:** Structured data accurately represents the visible UI.

## Test 3: Action Execution (Determinism)
- **Objective:** Verify field updates and command flow.
- **Tool Call 1 (Setup):** Navigate to a field.
- **Tool Call 2 (Action):**
  ```json
  {
    "name": "execute_action",
    "arguments": {
      "session_id": "0",
      "target_id": "wnd[0]/usr/txtRSYST-BNAME",
      "action_type": "set_text",
      "params": { "value": "AGENT_TEST" }
    }
  }
  ```
- **Tool Call 3 (Verification):**
  ```json
  { "name": "observe_screen", "arguments": { "session_id": "0" } }
  ```
- **Validation Logic:** The observation in Call 3 must show the field with value "AGENT_TEST".
- **Expected Outcome:** UI state matches the requested action.

## Test 4: Modal Safety (Guard Verification)
- **Objective:** Ensure actions fail gracefully when a modal is blocking.
- **Setup:** Manually trigger a modal dialog in SAP.
- **Tool Call:**
  ```json
  {
    "name": "execute_action",
    "arguments": {
      "session_id": "0",
      "target_id": "wnd[0]/tbar[0]/btn[0]",
      "action_type": "press"
    }
  }
  ```
- **Validation Logic:** Result should indicate failure or wait timeout because the main window is blocked.
- **Expected Outcome:** Runtime prevents interaction with the background window while modal is active.

## Test 5: Entity Extraction (Classification)
- **Objective:** Verify high-level entity mapping.
- **Tool Call:**
  ```json
  {
    "name": "extract_entity",
    "arguments": {
      "session_id": "0",
      "entity_type": "SalesOrder"
    }
  }
  ```
- **Validation Logic:** Returns structured fields (OrderNumber, Customer, etc.) mapped from raw controls.
- **Expected Outcome:** Semantic mapping works for known screen types.

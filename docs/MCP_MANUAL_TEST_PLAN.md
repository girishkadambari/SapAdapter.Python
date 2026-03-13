# MCP Manual Validation Plan

This document provides a step-by-step manual flow to verify the SAP MCP runtime.

## Test Suite 1: Connectivity & Discovery

### 1.1 Session Discovery
- **Tool:** `list_sessions`
- **Action:** Call the tool with no arguments.
- **Expected Output:** A list of active SAP sessions with IDs and Transaction names.
- **Validation Criteria:** Returns non-empty list if SAP is open.
- **Failure Scenario:** `Error: SAP GUI not running` or empty list when sessions exist.

### 1.2 Session Observation
- **Tool:** `observe_screen`
- **Action:** Call with `session_id`.
- **Expected Output:** JSON structure containing `title`, `transaction`, and list of `controls`.
- **Validation Criteria:** `title` matches the SAP window title; `controls` count is > 0.

## Test Suite 2: UI Interaction

### 2.1 Set Field Value
- **Tool:** `execute_action`
- **Params:** `action_type: "set_text"`, `target_id: "wnd[0]/usr/txt..."`, `params: {"value": "TEST_DATA"}`
- **Expected Output:** `Success: True`
- **Validation Criteria:** Check SAP GUI manually; the field should contain "TEST_DATA".

### 2.2 Button Press
- **Tool:** `execute_action`
- **Params:** `action_type: "press"`, `target_id: "wnd[0]/tbar[0]/btn[3]"` (Back button)
- **Expected Output:** `Success: True`
- **Validation Criteria:** SAP GUI window navigates back or screen changes.

## Test Suite 3: Advanced Extraction

### 3.1 Table Data Extraction
- **Tool:** `observe_screen` (Inspect metadata/controls)
- **Action:** Navigate to a transaction with a table (e.g., SU01, SE16).
- **Validation Criteria:** The `controls` list should contain items of type `GuiTableControl` or `GuiGridView` with row data in the `metadata`.

### 3.2 Modal Detection
- **Action:** Trigger a modal in SAP (e.g., click Exit without saving).
- **Tool:** `observe_screen`
- **Expected Output:** `modal: { "active": True, "text": "..." }`
- **Validation Criteria:** The `modal` object in the response correctly identifies the popup.

## Test Suite 4: Visuals

### 4.1 Screenshot Capture
- **Tool:** `observe_screen`
- **Params:** `include_screenshot: True`
- **Expected Output:** `screenshot_data` contains a long base64 string.
- **Validation Criteria:** Decode the string or check size > 10KB.

# MCP Tool Reference

This document describes the tools exposed by the SAP MCP Adapter to AI agents. All tools are prefixed with `sap_`.

## Session Tools

### `sap_list_sessions`
- **Description**: Discovers active SAP GUI windows and returns their session IDs.
- **When to use**: Call this first to identify which session to attach to.
- **Output**: A list of session objects including `sessionId`, `transaction`, `title`, and `user`.

## Observation Tools

### `sap_observe_screen`
- **Description**: Captures the complete state of the current SAP screen.
- **Parameters**: 
    - `session_id` (string, optional): The ID of the session to observe.
    - `include_screenshot` (boolean, optional): Whether to capture a visual snapshot.
- **Output**: A structured JSON object containing all controls (fields, buttons, labels), their types, values, and simplified technical IDs.

### `sap_inspect_control`
- **Description**: Provides detailed metadata for a specific control on the screen.
- **Parameters**:
    - `target_id` (string): The technical ID of the control.
- **Output**: Detailed properties, supported actions, and current value of the control.

### `sap_capture_visual`
- **Description**: Captures a high-resolution screenshot of the active window.
- **Output**: Base64 encoded image content.

## Action Tools

### `sap_execute_action`
- **Description**: Performs a specific action on a control.
- **Parameters**:
    - `action_type` (string): e.g., `press_button`, `set_field`, `select_tab`.
    - `target_id` (string): The ID of the control to act upon.
    - `parameters` (object): Additional data (e.g., `{ "value": "1000" }`).
- **Output**: Status of the execution (`success` or `error`).

### `sap_navigate`
- **Description**: Navigates to a specific SAP Transaction Code (T-Code).
- **Parameters**:
    - `t_code` (string): The transaction code (e.g., `VA03`, `MM02`).

## Specialized Tools

### `sap_extract_entity`
- **Description**: High-level tool to extract business-validated data objects from the screen.
- **Parameters**:
    - `entity_type` (string): The type of entity to extract (e.g., `sales_order`, `material`).
- **Output**: A domain-specific JSON object representing the business entity.

### `sap_get_sap_context`
- **Description**: Returns technical metadata about the current SAP system (System ID, Client, User, Language, etc.).

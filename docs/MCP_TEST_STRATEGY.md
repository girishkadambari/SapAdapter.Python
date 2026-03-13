# SAP MCP Testing Strategy

This document outlines the strategy for validating the SAP MCP server using Postman.

## Objectives
- **Functional Correctness**: Ensure all MCP tools (Observe, Execute, Extract) perform as expected across different SAP screen types.
- **Stability**: Verify that deterministic waiting and safety guards (BusyGuard, ModalGuard) prevent race conditions.
- **Regression Testing**: Provide a repeatable suite of tests to run after any architectural changes.
- **Data Integrity**: Validate that complex controls (Grids, Trees, Tables) are serialized correctly into structured JSON models.

## Testing Architecture
To keep the production runtime clean, we use a **Local HTTP Test Adapter** (`tests/postman_adapter.py`). 

- **Production Core**: Remains untouched, continuing to serve WebSockets.
- **Test Adapter**: A thin layer that maps HTTP POST requests from Postman to the same internal `McpServer` and `CommandRouter` used by production.
- **Tool Parity**: Every action available via MCP WebSockets is exposed via HTTP `/mcp`.

## What to Test
### 1. Runtime Level
- Session lifecycle (List, Attach).
- Protocol compliance (JSON-RPC 2.0).
- Error handling (Invalid IDs, malformed JSON).

### 2. Screen Context Level
Tests should be run while the SAP GUI is positioned on specific window types:
- **Form Screens**: Test field extraction and text input.
- **Grid Screens**: Test row extraction and double-clicking.
- **Tree Screens**: Test node expansion and selection.
- **Modal Screens**: Test blocking behavior and button confirmation.

## Manual vs. Automated
| Category | Method | Tool |
|----------|---------|------|
| Protocol / Schema | Automated | Postman |
| Control Data Integrity | Automated | Postman |
| Visual UI Layout | Manual | Visual Inspection / Screenshot Tool |
| Agent Reasoning | Manual | LLM / Prompts |

## Best Practices
- **Environment Variables**: Always use `{{base_url}}` and `{{session_id}}` to avoid hardcoding.
- **Teardown**: Ensure actions don't leave the SAP GUI in a broken state (e.g., leaving a transaction open).
- **Wait Strategies**: The server has built-in waiting, but Postman tests should allow for SAP network latency.

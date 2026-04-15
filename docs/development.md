# Development Guide

This document is for developers who want to extend the SAP MCP Adapter or contribute to its core.

## Project Structure

- `sap_mcp/core`: Configuration and basic types.
- `sap_mcp/runtime`: SAP GUI interaction logic (COM).
- `sap_mcp/mcp`: MCP Protocol implementation and tool registration.
- `sap_mcp/observation`: Logic for building structured snapshots.
- `sap_mcp/execution`: Action dispatching and safety guards.

## Adding a New Tool

1. **Create a Tool Class**: Inherit from `BaseMcpTool` in `sap_mcp/mcp/tools/`.
2. **Define Schema**: Implement `name`, `description`, and `input_schema`.
3. **Implement Logic**: Implement `execute()`.
4. **Register**: Add the tool instance to `McpAdapter._register_tools()` in `sap_mcp/mcp/mcp_adapter.py`.

## Running the Development Servers

### Stdio Mode
```bash
python mcp_stdio.py
```

### WebSocket Mode
```bash
python main.py
```

## Testing Locally

Currently, we use a manual strategy with diagnostic scripts:
1. `scripts/diag_enricher.py`: Tests the `ControlEnricher` logic.

### MCP Client Testing
The best way to test the full stack is to use an MCP client like **Claude Desktop** or an MCP Inspector.

## TODO: Automated Testing
We are working on implementing a `pytest` suite. Contributions in this area are highly valued.
- Aim for 80%+ coverage of the `sap_mcp/mcp` and `sap_mcp/observation` packages.
- Need mocks for SAP COM objects to allow testing on Linux/CI.

# MCP Server Configuration Guide

This guide provides the necessary configuration snippets to add the SAP MCP Adapter to various MCP-compliant clients.

## 1. Claude Desktop

Add the following to your `claude_desktop_config.json` (typically located at `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "sap-adapter": {
      "command": "python",
      "args": [
        "C:\\path\\to\\SapAdapter.Python\\mcp_stdio.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\SapAdapter.Python"
      }
    }
  }
}
```
*Note: Ensure you replace `C:\\path\\to\\SapAdapter.Python` with the absolute path to your cloned repository. We recommend using the full path to your virtual environment's python executable (e.g., `C:\\path\\to\\venv\\Scripts\\python.exe`).*

---

## 2. Cursor

To integrate with Cursor IDE:

1.  Open **Cursor Settings** -> **General** -> **MCP**.
2.  Click **+ Add New MCP Server**.
3.  Fill in the details:
    *   **Name**: `SAP`
    *   **Type**: `command`
    *   **Command**: `python C:\path\to\SapAdapter.Python\mcp_stdio.py`

*Note: If you are running the adapter as a WebSocket server (using `main.py`), use:*
*   **Type**: `SSE`
*   **URL**: `http://localhost:8787`

---

## 3. Antigravity

To register this server with Antigravity (or similar coding assistants):

Add this to your workspace configuration or directly prompt the assistant with:

```markdown
"Use the following MCP server via stdio:
Command: python
Args: [\"C:\\path\\to\\SapAdapter.Python\\mcp_stdio.py\"]"
```

If using the **Antigravity Extension** configuration:

```json
{
  "antigravity.mcpServers": [
    {
      "name": "SAP MCP",
      "transport": "stdio",
      "command": "python",
      "args": ["C:\\path\\to\\SapAdapter.Python\\mcp_stdio.py"]
    }
  ]
}
```

---

## 🔧 Environment Variables

The adapter honors the following environment variables (defined in your `.env` file):

- `PORT`: (Default: 8787) Port for WebSocket/SSE transport.
- `HOST`: (Default: 127.0.0.1) Host interface to bind to.
- `LOG_LEVEL`: (DEBUG, INFO, WARNING, ERROR) Controls logging verbosity.

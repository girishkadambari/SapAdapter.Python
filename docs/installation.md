# Installation & Environment Setup

This guide walks you through the requirements and steps to get the SAP MCP Adapter running on your Windows machine.

## Prerequisites

### 1. Windows Operating System
The adapter relies on SAP GUI for Windows COM automation, which is only available on Windows. It has been tested on Windows 10 and 11.

### 2. SAP GUI for Windows
You must have a working installation of SAP GUI (7.70, 8.00, or later).

### 3. Server-Side Scripting Configuration
For the adapter to interact with SAP, you must enable scripting on the SAP server (RZ11).
- Set `sapgui/user_scripting` to `TRUE`.
- *Note: If you don't have administrative access to the SAP server, ensure this is enabled for your development environment.*

### 4. Client-Side Scripting Configuration
Enable scripting in your local SAP GUI options:
1. Open **SAP GUI Options**.
2. Navigate to **Accessibility & Scripting** > **Scripting**.
3. Check **Enable scripting**.
4. (Optional but Recommended) Uncheck **Notify when a script attaches to SAP GUI**.
5. (Optional but Recommended) Uncheck **Notify when a script opens a connection**.

## Installation Steps

### 1. Python Environment
We recommend using Python 3.10 or higher.

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory (you can copy `.env.example`).

```bash
copy .env.example .env
```

Default settings:
- `PORT`: 8787 (for WebSocket server)
- `LOG_LEVEL`: INFO

## Verifying the Installation

To verify that the adapter can connect to SAP GUI:

1. Open SAP GUI and log into a system.
2. Run the diagnostic script:
   ```bash
   python scripts/diag_enricher.py
   ```
3. If successful, you should see output showing "Enriched actions" for a test control.

## MCP Client Integration

### Claude Desktop
Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sap": {
      "command": "C:\\path\\to\\your\\venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\sap-mcp-adapter\\mcp_stdio.py"]
    }
  }
}
```
Replace the paths with your actual local paths.

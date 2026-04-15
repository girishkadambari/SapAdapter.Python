# Getting Started

Welcome to the SAP MCP Adapter! This guide will help you understand the basics of the project and how to get your first AI agent interacting with SAP.

## 1. High-Level Concept

The SAP MCP Adapter acts as a "remote control" for SAP GUI.
- **AI Agents** (like Claude) send commands (e.g., "Find the Sales Order 12345").
- **MCP Adapter** translates these into SAP GUI scripting actions.
- **SAP GUI** executes the actions and returns the new screen state.
- **MCP Adapter** captures the state and sends a structured report back to the agent.

## 2. Quick Setup Checklist

1. **Environment**: Ensure you are on Windows and have SAP GUI for Windows installed.
2. **Configuration**: Enable scripting in SAP GUI Options and on the SAP Server.
3. **Execution**:
    - Run `python mcp_stdio.py` for CLI/Stdio usage.
    - Run `python main.py` for WebSocket usage.

Detailed instructions can be found in the [Installation Guide](installation.md) and the [MCP Configuration Guide](mcp-configuration.md).

## 3. Your First Tools

Once attached, your agent will primarily use these tools:
- **`sap_list_sessions`**: To find out which SAP window is active.
- **`sap_observe_screen`**: To see what is currently on the screen.
- **`sap_execute_action`**: To interact with fields and buttons.

## 4. Project Status & Maturity

- **Current Version**: v1.0.0-beta
- **Maturity**: Functional/Production-grade core logic.
- **Support**: Community-driven via GitHub Issues.

### Honest Assessment
- **Reliability**: High for standard SAP UI elements (TextFields, Buttons).
- **Complexity**: High for complex grids (ALV) or custom controls (Shells).
- **Platform**: Strictly Windows-only due to dependency on Win32 COM.

## 5. Security & Responsibility

Automating ERP systems like SAP requires caution:
- Always test actions in a **Quality/Development** system before moving to Production.
- Monitor your agent's logs to ensure it isn't making unexpected changes.
- Ensure the user account used by SAP GUI has the appropriate (and limited) permissions for the tasks it will perform.

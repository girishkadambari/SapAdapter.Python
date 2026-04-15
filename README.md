# SAP MCP Adapter

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-green.svg)](https://modelcontextprotocol.io)

**SAP MCP Adapter** is a production-grade interface that bridges AI agents with SAP GUI for Windows using the Model Context Protocol (MCP). It provides a deterministic, structured, and safe way for models to navigate SAP, observe screen states, and execute complex business transactions.

## 🚀 Key Features

- **Protocol Compliant**: Full support for Model Context Protocol (MCP) for seamless integration with Claude Desktop, IDEs, and custom AI agents.
- **Deterministic Interaction**: High-reliability action pipeline with built-in safety guards (`WaitStrategy`, `BusyGuard`).
- **Structured Observation**: Converts raw SAP COM hierarchies into clean, typed Pydantic models.
- **Visual reasoning**: High-quality screenshot support for debugging and Vision-Language Model (VLM) analysis.
- **Intelligent Classification**: Automatically categorizes screens (Search, Detail, Grid) to guide agent behavior.
- **Business Entity Extraction**: Domain-aware data extraction (e.g., Sales Orders, Material Master) directly from the GUI.

## 📦 Quickstart

### Prerequisites

- **Windows OS** (Required for SAP GUI Scripting).
- **SAP GUI for Windows** installed and configured.
- **Scripting Enabled**: SAP GUI Options -> Accessibility & Scripting -> Scripting -> "Enable scripting" (checked).

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/sap-mcp-adapter.git
   cd sap-mcp-adapter
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   pip install -r requirements.txt
   ```

3. Configure your environment:
   ```bash
   cp .env.example .env
   ```

### Running the Server

#### Over Stdio (Recommended for MCP Clients)
```bash
python mcp_stdio.py
```

#### Over WebSockets
```bash
python main.py
```

## 🛠 MCP Tools

The adapter exposes several tools to AI agents:

- `sap_list_sessions`: Discover active SAP GUI windows.
- `sap_observe_screen`: Capture current screen state (controls, status bar, modals).
- `sap_execute_action`: Perform clicks, text entry, or selections.
- `sap_extract_entity`: Retrieve business-validated data objects.
- `sap_capture_visual`: Capture a high-resolution screenshot of the active window.

## 📖 Documentation

- [Getting Started](docs/getting-started.md)
- [Installation & Setup](docs/installation.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [MCP Configuration Guide](docs/mcp-configuration.md)
- [MCP Tool Reference](docs/mcp-tools.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [FAQ](docs/faq.md)
- [Development Guide](docs/development.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## ⚠️ Responsible Usage & Safety

Automating SAP GUI actions carries inherent risks. Please observe the following guardrails:

- **Non-Production First**: Always develop and test your agentic workflows in a **Sandbox** or **Development** environment. Never point an autonomous agent at a Production system without extreme caution and human-in-the-loop validation.
- **Destructive Actions**: The adapter can execute any action the logged-in user has permission for. Ensure your agent is aware of the consequences of pressing buttons like "Save", "Delete", or "Post".
- **Read-Only Mode**: For data extraction tasks, consider using a SAP user with read-only permissions to mitigate risk.
- **Session Awareness**: The adapter interacts with the *active* session. Be mindful of multi-session environments to avoid unintended actions in the wrong window.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---
*Disclaimer: This project is not affiliated with, sponsored by, or endorsed by SAP SE.*

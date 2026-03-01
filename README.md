# SAP Copilot Adapter (Python Edition)

A high-performance, stable SAP GUI Adapter built in Python. This adapter overcomes the complex COM threading and architecture issues often found in C# implementations by leveraging `pywin32` for direct and reliable SAP GUI scripting access.

## Features

- **Robust COM Discovery**: Replicates native VBScript logic for guaranteed connection to SAP GUI.
- **Full Protocol Parity**: Supports `healthCheck`, `listSessions`, `attachSession`, `captureSnapshot`, and `executeCommand`.
- **SAP Agent Primitives**: Comprehensive support for:
  - **Grid Control (ALV)**: Summary, Row extraction, and Filtered searches.
  - **Table Control**: Summary, Row reading, and Searching.
  - **Tree Control**: Node discovery, Filtering, and Selection.
  - **Menu Bar**: Path listing and Selection.
- **Live Sync**: Background monitoring of SAP screen changes with WebSocket event broadcasting (`screen.changed`).
- **Safety First**: modal dialog detection and robust wait-for-idle (busy state) logic.
- **Production Ready**: Structured logging with rotation, SRP-based architecture, and async/await for high concurrency.

## Project Structure

```text
SapAdapter.Python/
├── main.py              # Application entry point & request routing
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
├── app/
│   ├── server.py        # Async WebSocket server implementation
│   ├── logger.py        # Loguru-based production logging config
│   ├── engine/          # Core SAP COM integration
│   │   ├── sap_engine.py   # SAP GUI discovery and session helpers
│   │   └── wait_helper.py  # Busy-state polling (Wait for Idle)
│   ├── models/          # Pydantic data models for the protocol
│   ├── snapshot/        # Complex screen capture pipeline
│   └── commands/        # Command Router and Action Handlers
│       ├── router.py       # High-level request router
│       └── handlers/       # Domain-specific action primitives
```

## Setup & Installation

### Prerequisites
- Python 3.9 or higher
- Windows OS (Required for SAP GUI COM)
- SAP GUI for Windows installed with "Scripting" enabled in options

### Installation
1. Navigate to the project directory:
   ```bash
   cd SapAdapter.Python
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Adapter

Start the adapter using the following command:
```bash
python main.py
```
The adapter will start a WebSocket server on port `8787` (default) and wait for connections from the Electron App.

## Development

- **Architecture**: The project follows the Single Responsibility Principle (SRP). All SAP actions are isolated in `app/commands/handlers/`.
- **Protocol**: The JSON protocol matches the `shared/protocol` definitions in the `sap-copilot-main` repository.
- **Logging**: Logs are written to the console and to `logs/adapter.log` with weekly rotation.

## License
Proprietary - Part of SAP Copilot Suite

# SAP MCP Server

A production-grade, deterministic SAP GUI scripting runtime and Model Context Protocol (MCP) server.

## Overview

This server provides AI agents with a reliable, structured interface for interacting with SAP GUI for Windows. It solves common automation challenges such as busy states, modal dialogs, and complex control trees by providing high-performance observers and deterministic action executors.

## Key Features

- **Protocol Compliant**: Full support for Model Context Protocol (MCP) and legacy JSON-RPC.
- **Deterministic Execution**: Action pipeline with built-in safety guards (`WaitStrategy`, `BusyGuard`).
- **Structured Observation**: Converts raw SAP COM trees into clean, typed Pydantic models.
- **Visual Capture**: High-quality screenshot support for debugging and VLM reasoning.
- **Functional Extraction**: High-level services to extract validated business entities (e.g., Sales Orders).
- **Intelligent Classification**: Automatically categorizes screens (Search, Detail, Grid) to guide agent behavior.

## Installation

### Prerequisites
- Windows OS (Required for SAP GUI Scripting)
- SAP GUI for Windows installed
- "Scripting" enabled in SAP GUI Options -> Accessibility & Scripting -> Scripting

### Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   python main.py
   ```

## Usage (MCP Tools)

The server exposes several tools for AI agents:

- `list_sessions`: Discover active SAP GUI windows.
- `observe_screen`: Capture current screen state (controls, status bar, modals).
- `execute_action`: Perform clicks, text entry, or selections on specific controls.
- `extract_entity`: Retrieve business-validated data objects from the screen.

## Project Structure

- `sap_mcp/runtime`: Session management and COM execution safety.
- `sap_mcp/observation`: Logic for building structured screen snapshots.
- `sap_mcp/controls`: Specialized handlers for fields, tables, grids, and shells.
- `sap_mcp/execution`: Deterministic action pipelines and wait strategies.
- `sap_mcp/extraction`: Business-level data extractions and validation.
- `sap_mcp/classification`: Screen pattern recognition.
- `sap_mcp/mcp`: MCP protocol adapter and server logic.

## License
Proprietary - Part of SAP Copilot Suite

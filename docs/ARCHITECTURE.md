# SAP MCP Server Architecture

This document provides a deep dive into the technical design of the SAP MCP Server.

## Core Philosophy

SAP GUI Scripting is notoriously brittle due to:
1. **Asynchronous UI States**: SAP might be busy processing even if the scripting engine is available.
2. **Modal Windows**: Blocking popups that prevent normal interaction.
3. **Complex Control Trees**: Hierarchies that are difficult to navigate for LLMs.

The SAP MCP Server solves these by providing a **Deterministic Runtime Wrapper** around the raw COM API.

## Layered Architecture

### 1. Runtime Layer (`sap_mcp/runtime`)
- **ComExecutor**: Serializes access to the COM thread to prevent threading deadlocks.
- **BusyGuard**: Polls the SAP session state to ensure the UI is idle before any action.
- **ModalGuard**: Detects and identifies blocking popups.

### 2. Observation Pipeline (`sap_mcp/observation`)
- **RawSnapshotBuilder**: Captures the raw COM hierarchy.
- **NormalizedSnapshotBuilder**: Simplifies raw data into typed `Control` models.
- **ScreenObservationBuilder**: Combines controls, status bar, and screenshots into a single atomic observation.

### 3. Control Handling (`sap_mcp/controls`)
- uses a **Registry Pattern** to route different SAP types (e.g., `GuiGridView`, `GuiTableControl`) to specialized handlers.
- Each handler knows exactly how to extract data from its specific control type.

### 4. Execution Pipeline (`sap_mcp/execution`)
- **ActionDispatcher**: Routes standardized `ActionRequest` objects.
- **WaitStrategy**: Implements deterministic waiting logic after every action.

### 5. Extraction & Classification
- **Extraction Layer**: Heuristics to map flat controls to business entities.
- **Classification Engine**: Recognizes UI patterns to provide higher-level context.

## MCP Protocol
The server implements the Model Context Protocol (MCP) over WebSockets, allowing it to serve as a high-fidelity toolset for ANY AI agent capable of using the protocol.

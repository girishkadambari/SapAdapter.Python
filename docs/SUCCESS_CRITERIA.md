# SAP MCP Success Criteria

The SAP MCP runtime is declared "Production-Ready" when it meets the following criteria:

## 1. Reliability & Stability
- [ ] **Session Recovery:** The server can reconnect to the SAP Scripting Engine after a network blip or SAP GUI restart.
- [ ] **Zero-Hang COM Calls:** No single tool call causes the server to hang indefinitely; all calls honor the `TimeoutPolicy`.
- [ ] **Modal Safety:** Actions are automatically blocked or queued when a modal dialog is present, preventing "Window is busy" COM errors.

## 2. Extraction Accuracy
- [ ] **Control Parity:** 100% of visible input fields and buttons on a standard "Easy Access" screen are captured in the `observe_screen` output.
- [ ] **Structured Navigation:** Tables and Grids are extracted with correct row/column headers.
- [ ] **Visual Alignment:** The `screenshot_data` matches the structured `controls` coordinates exactly (no offset errors).

## 3. Action Determinism
- [ ] **Post-Action Verification:** After an `execute_action` call, the returned `observation` must reflect the change (e.g., text set or button pressed).
- [ ] **Wait for Idle:** The execution pipeline correctly waits for the SAP status bar "Ready" state before returning.

## 4. Agent Compatibility
- [ ] **Tool Success Rate:** An AI agent (e.g., Antigravity) can successfully perform a multi-step transaction (e.g., "Check User Status") with a >95% success rate.
- [ ] **Error Clarity:** Tool errors provide actionable feedback to the agent (e.g., "Field wnd[0]/... not found").

## 5. Performance
- [ ] **Observation Latency:** `observe_screen` (without screenshot) returns in < 500ms on a standard VM.
- [ ] **Command Latency:** `execute_action` returns shortly after the SAP GUI becomes idle.

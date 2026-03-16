# Playbook: Status Validation

## Objective
Go beyond "it didn't crash" and verify business logic correctness.

## 1. Status Bar Interpretation
- **Message Types**:
  - `S` (Success): Green light.
  - `W` (Warning): Orange. Might need an extra Enter to bypass.
  - `E` (Error): Red light. Action failed. Stop.
  - `I` (Information): Gray/Blue. Informational modal.

## 2. Deep Status Check (`get_status_and_incompletion`)
Use this tool after "Save" or "Check" actions in complex transactions (VA01, ME21N).
- **Document Status**: Is it "Released", "Blocked", or "Completed"?
- **Incompletion Log**: Are there missing fields preventing the document from being saved?
  - Extract the list of missing fields.
  - Report them specifically.

## 3. Validation Logic
- If `sap_navigate(send_vkey=11)` (Save) returns "Document X saved", confirm via `get_sap_context`.
- If a warning appears (e.g., "Credit limit exceeded"), log it as a `VALIDATION_WARNING`.

## 4. Recovering from Errors
- If an Error message blocks navigation, you must fix the field mentioned in the message text or `Cancel` the transaction.
- Do not attempt to navigate away via `/n` if an "Exit without saving?" popup is expected without handling that popup.

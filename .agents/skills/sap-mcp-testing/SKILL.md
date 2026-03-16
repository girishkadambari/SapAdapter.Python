---
name: SAP MCP Test Operator
description: Advanced operating principles and execution loops for testing SAP MCP tools and workflows.
---

# SAP MCP Test Operator

## Purpose
This skill transforms Antigravity into a precision testing lab for SAP MCP. It defines how an agent should observe, act, and validate when interacting with SAP GUI to ensure tool reliability and catch regressions.

## Operating Principles
1. **Never Assume Success**: Every technical success (tool returned OK) must be semantically validated (did the SAP screen actually change as expected?).
2. **Context First**: Always use `sap_get_screen_summary` before any action. If indices or IDs have shifted, the plan must abort and re-evaluate.
3. **Inspect Before Commit**: For complex controls (Tables/Grids), use `sap_inspect_control` to verify metadata before sending values.
4. **Safety Over Speed**: If a control ID is ambiguous or a popup is unexpected, stop and report. Do not guess.
5. **Traceable Steps**: Every action must be recorded with its "Why", "How", and "Observed Result".

## Execution Loop (OSID-VLC)
Follow this loop for every atomic interaction:

1. **Observe**: Run `sap_get_screen_summary` to get the current state.
2. **Summarize**: Describe what is on the screen and identify the target control.
3. **Inspect**: (Optional) Run `sap_inspect_control` for critical fields or table cells.
4. **Decide**: Select the specific tool and payload.
5. **Execute**: Call the MCP tool.
6. **Validate**: Run `sap_get_screen_summary` (or `sap_capture_visual`) to verify the effect.
7. **Log**: Record the step in the structured output format.
8. **Continue/Stop**: Proceed to the next step or stop on failure/ambiguity.

## Tool Usage Guide
| Tool | Best Used For | Post-Action Validation |
| :--- | :--- | :--- |
| `sap_navigate` | T-Codes, Enter, Save, Back | Verify `Title` or `Program` changed. |
| `sap_interact_field` | Simple Inputs, Checkboxes | Verify `Value` attribute in summary. |
| `sap_table_action` | ALV Grids, TableControls | Check specific cell data or row selection. |
| `sap_search_help_select` | F4 Hit Lists | Verify source field now contains selection. |
| `sap_execute_batch` | Filling a screen form | Final screen summary check. |

## Failure Diagnosis Rules
When a step fails:
- **Classify**: Use `failure-diagnosis.md` to categorize (e.g., `FIELD_INTERACTION_FAILURE`).
- **Capture**: Call `sap_capture_visual` to see exactly what SAP shows.
- **Inspect**: Run `sap_inspect_control` on the target to see if the ID changed.
- **Report**: Detail the "Likely failure layer" (MCP/Scripting/Network/SAP-State).

## Recommended Output Format
```markdown
- **Step**: [Sequence Number]
- **Intent**: [What are we trying to achieve?]
- **Tool Chosen**: [Tool Name]
- **Why**: [Rationale based on observation]
- **Input**: [Payload data]
- **Observed Result**: [Immediate response from tool]
- **Validation Result**: [Results from post-action check]
- **Status**: [SUCCESS/FAILURE/WARNING]
- **Failure Layer**: [If failed, where?]
- **Next Action**: [What follows?]
```

## Safety Rules
- Do not use `send_vkey(0)` (Enter) to bypass error messages without analyzing the message text in the status bar.
- Do not attempt to scroll tables by guessing row counts; use `sap_inspect_control` to get total row counts and page sizes.
- Always check `get_status_and_incompletion` after "Save" or "Next Screen" actions.

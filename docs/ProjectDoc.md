SAP MCP Server
Production Architecture & Design Specification

Version: 1.0
Author: Girish
Status: Architecture Design
Purpose: Build a scalable open-source SAP GUI automation runtime using MCP.

1. Project Overview
1.1 Project Name

SAP MCP Server

A production-grade Model Context Protocol (MCP) server designed to provide deterministic SAP GUI automation capabilities to AI agents.

This runtime enables LLM-based agents to:

observe SAP GUI screens

analyze UI state

extract business data

perform actions

verify outcomes

reason using screenshots

The MCP server acts as the execution runtime layer between AI agents and SAP GUI.

2. Problem Statement

SAP GUI is:

stateful

complex

modal-driven

not designed for automation

inconsistent in control exposure

Traditional SAP automation fails because:

scripts break on minor changes

flows are hardcoded

error handling is weak

UI state is poorly understood

The goal is to build a deterministic SAP runtime that AI agents can safely use.

3. Goals
Primary Goals

Build a scalable MCP server that can:

Observe SAP GUI state

Extract structured UI data

Execute deterministic actions

Verify results after actions

Provide screenshot-based context

Support multi-agent orchestration

Work across many SAP transactions

Non-Goals

The MCP server will NOT:

implement business workflows

contain LLM reasoning

contain domain-specific SAP flows

contain UI logic

Those belong to agent layer / Electron UI.

4. System Architecture
High Level Architecture
+------------------------------------------------------+
|                   Electron UI                        |
|------------------------------------------------------|
| Chat UI                                              |
| Task Workspace                                       |
| Multi-Agent Orchestrator                             |
| Planner / Screen Understanding / Extraction Agents   |
| Screenshot Timeline                                  |
+---------------------------+--------------------------+
                            |
                            | MCP Protocol
                            |
+------------------------------------------------------+
|                 SAP MCP Python Server                |
|------------------------------------------------------|
| Runtime Layer                                        |
| Observation Engine                                   |
| Control Handlers                                     |
| Extraction Engine                                    |
| Screenshot Service                                   |
| Action Executor                                      |
| Validation Engine                                    |
| Screen Classifier                                    |
+------------------------------------------------------+
                            |
                            |
                       SAP GUI (COM)
                            |
                            |
                        SAP Backend
5. Core Design Principles
Deterministic Runtime

All SAP actions must follow:

observe → act → verify
Capability-Based Tools

MCP exposes capabilities, not workflows.

Example:

Good:

set_field
press_button
get_table_rows
capture_screenshot

Bad:

analyze_invoice_block
debug_credit_issue
Structured Observation

Agents never interact with raw SAP controls.

Instead they receive a normalized:

ScreenObservation
Component Abstraction

Each SAP control type has its own handler.

Examples:

Field

Button

Table

Grid

Tree

Tab

Modal

Toolbar

Menu

Validation First

Every extraction includes:

confidence

completeness

actionability

freshness

6. MCP Tool Philosophy

Agents should be able to perform what humans can do in SAP.

Human Interaction Types

Navigation
Field editing
Table browsing
Popup handling
Menu navigation
Data inspection

7. MCP Tool Surface
Observation Tools
list_sessions
attach_session
get_current_observation
get_visible_controls
get_status_bar
get_active_modal
capture_screenshot
diff_last_observation
Action Tools
navigate_tcode
set_field
get_field
press_button
send_vkey
select_tab
select_menu_path
select_table_row
double_click_grid_row
confirm_modal
cancel_modal
Extraction Tools
extract_form
extract_table
extract_grid
extract_business_entities
Verification Tools
wait_for_idle
verify_expected_state
wait_for_screen_change
8. Core Data Contracts

These schemas define the system's language.

8.1 Control Schema

Represents one SAP UI component.

class Control:
    id: str
    type: str
    subtype: str
    label: Optional[str]
    value: Optional[str]
    editable: bool
    enabled: bool
    visible: bool
    required: bool
    parent_id: Optional[str]
    bounds: Optional[Tuple[int,int,int,int]]
    actions: List[str]
    confidence: float
8.2 ScreenObservation

Represents the current screen.

class ScreenObservation:
    session_id: str
    transaction: str
    title: str
    program: Optional[str]
    status_bar: StatusBar
    modal: Optional[Modal]
    controls: List[Control]
    tables: List[TableSummary]
    grids: List[GridSummary]
    screenshot_ref: Optional[str]
    validation_summary: ValidationSummary
8.3 ActionRequest
class ActionRequest:
    action_type: str
    target: Dict
    input: Dict
    session_id: str
    expected_state: Optional[Dict]
8.4 ActionResult
class ActionResult:
    ok: bool
    action: str
    target: str
    effects: Dict
    new_observation: ScreenObservation
    warnings: List[str]
    confidence: float
8.5 BusinessExtraction
class BusinessExtraction:
    entity_type: str
    data: Dict
    source_controls: List[str]
    completeness: str
    confidence: float
9. Folder Structure
sap_mcp/
│
├── server/
│   ├── mcp_server.py
│   ├── tool_router.py
│   ├── request_context.py
│
├── runtime/
│   ├── sap_runtime.py
│   ├── session_manager.py
│   ├── com_executor.py
│   ├── busy_guard.py
│   ├── modal_guard.py
│
├── controls/
│   ├── control_registry.py
│   ├── base_handler.py
│   ├── field_handler.py
│   ├── button_handler.py
│   ├── table_handler.py
│   ├── grid_handler.py
│   ├── tree_handler.py
│   ├── modal_handler.py
│   ├── toolbar_handler.py
│   ├── menu_handler.py
│
├── observation/
│   ├── raw_snapshot_builder.py
│   ├── normalized_snapshot_builder.py
│   ├── screen_observation_builder.py
│   ├── observation_diff.py
│
├── extraction/
│   ├── form_extractor.py
│   ├── table_extractor.py
│   ├── grid_extractor.py
│   ├── entity_extractor.py
│   ├── semantic_enricher.py
│   ├── validation_engine.py
│
├── actions/
│   ├── action_executor.py
│   ├── action_validator.py
│   ├── action_verifier.py
│   ├── navigation_actions.py
│   ├── field_actions.py
│   ├── grid_actions.py
│   ├── modal_actions.py
│
├── vision/
│   ├── screenshot_service.py
│   ├── region_cropper.py
│   ├── screenshot_diff.py
│
├── screen/
│   ├── screen_classifier.py
│   ├── screen_registry.py
│   ├── handlers/
│   │   ├── generic_form_screen.py
│   │   ├── generic_table_screen.py
│   │   ├── generic_modal_screen.py
│
├── schemas/
│   ├── control.py
│   ├── observation.py
│   ├── action_request.py
│   ├── action_result.py
│   ├── extraction.py
│   ├── validation.py
│
├── utils/
│   ├── logging.py
│   ├── retry.py
│   ├── timers.py
│
└── tests/
    ├── runtime_tests.py
    ├── extraction_tests.py
    ├── action_tests.py
10. Action Execution Pipeline

Every action follows the same lifecycle.

1 Validate request
2 Resolve control
3 Wait for SAP idle
4 Execute action
5 Wait for screen settle
6 Capture new observation
7 Verify expected state
8 Return ActionResult
11. Screenshot Service

Used for:

visual reasoning

debugging

timeline

screen diffing

Features:

capture_screenshot
capture_region
diff_last_screenshot
annotate_regions
12. Screen Classification

Used by agents to understand current screen.

Examples:

GenericFormScreen
GenericTableScreen
ModalScreen
ALVGridScreen
MIROScreen (optional domain layer)
13. Validation Model

Each extraction must include:

Dimension	Description
Presence	Control exists
Readable	Value extracted
Actionable	Agent can interact
Semantic	Meaning understood
Complete	Full entity extracted
Fresh	Data from latest observation
14. Logging Standard

Use structured logging.

Example:

INFO action_executor.execute
session=1
action=set_field
target=BKPF-BUKRS
value=1000
15. Error Handling

Never crash MCP server.

Return structured errors:

ControlNotFound
SessionNotAttached
ModalBlockingAction
TimeoutWaitingForIdle
ActionVerificationFailed
16. Coding Standards

Follow these standards:

Python

Python ≥ 3.11

Type hints mandatory

Pydantic for schemas

Black formatting

Ruff linting

Code Rules

Single Responsibility Principle

Max function length: 50 lines

Dependency injection preferred

Avoid global state

No LLM calls inside MCP

17. Testing Strategy
Unit Tests
control extraction
table parsing
action validation
Integration Tests
attach session
navigate tcode
field edit
modal handling
End-to-End Tests
open SAP
navigate
fill fields
verify outcome
18. Implementation Plan
Phase 1

Core contracts

Control

ScreenObservation

ActionRequest

ActionResult

Phase 2

Runtime layer

session manager

COM executor

idle wait

modal detection

Phase 3

Observation engine

control extraction

status bar

modal

screenshot capture

Phase 4

Action executor

navigation

field editing

button click

verification

Phase 5

Extraction engine

form

table

grid

entity extraction

Phase 6

Screen classification

Phase 7

Agent integration (Antigravity)

Phase 8

Electron UI workspace

19. Future Extensions

Possible enhancements:

SAP Fiori automation

Playwright integration

distributed MCP cluster

enterprise auth

audit logs

workflow memory

20. Success Criteria

The MCP server is successful if:

agents can reliably execute SAP actions

screen state is correctly observed

actions are verified

screenshots align with state

system supports many SAP transactions

21. Final Vision

SAP MCP server becomes:

The deterministic execution layer for SAP agents.

Agents provide reasoning.

MCP provides capability, reliability, and safety.
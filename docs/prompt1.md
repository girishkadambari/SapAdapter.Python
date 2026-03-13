You are a senior Python architect and SAP GUI scripting expert.

Your task is to refactor my existing SAP MCP server incrementally into a production-grade deterministic SAP runtime.

IMPORTANT:
Do NOT do one giant rewrite at once.
Do NOT break the whole project in one pass.
Do NOT delete working behavior unless you replace it with a better structured equivalent.

You must execute this refactor in safe, reviewable phases with small coherent commits.

You must follow the architecture defined in:
- SAP_MCP_ARCHITECTURE.md
- SAP_MCP_PROJECT.md

I will also provide the SAP GUI Scripting API PDF. Use it as the primary source for control APIs and supported interactions.

==================================================
PRIMARY GOAL
==================================================

Refactor the existing MCP server into a scalable, open-source style SAP GUI scripting runtime that supports:

- session attach/discovery
- deterministic action execution
- structured screen observation
- screenshot capture
- proper control abstraction
- field/button/tab/menu support
- table/grid/tree/shell support
- modal/status handling
- filtering and row finding
- validation and action verification
- MCP tools suitable for AI agents

This server must support all common human SAP GUI interactions.

==================================================
NON-GOALS
==================================================

Do NOT:
- implement business-specific workflows
- hardcode MIRO/OTC logic into MCP core
- add LLM calls into MCP server
- build unit tests right now
- optimize prematurely for UI polish
- create giant god classes

==================================================
REFACTOR STRATEGY
==================================================

You must work in phases.

For each phase:
1. inspect current code
2. identify what can be preserved
3. refactor incrementally
4. keep imports clean
5. keep code compiling/runnable
6. summarize changes made
7. list follow-up TODOs

At the end of every phase, provide:
- files created
- files modified
- files deprecated
- architectural reasoning
- remaining gaps

==================================================
GLOBAL ENGINEERING RULES
==================================================

1. Prefer composition over giant inheritance trees
2. Use explicit types everywhere
3. Keep methods short and readable
4. Add docstrings to public classes and methods
5. Add comments only where they genuinely help understanding
6. Use structured logging
7. Centralize retries / waits / modal handling
8. Never mix websocket/MCP routing with SAP logic
9. Never mix extraction with action execution
10. Every action must return structured ActionResult
11. Every observation must return structured ScreenObservation
12. Follow open-source friendly folder structure and naming
13. Do not leave dead code if a cleaner migration path exists
14. Use TODO markers only for truly deferred features

==================================================
TARGET STRUCTURE
==================================================

sap_mcp/
  server/
  runtime/
  controls/
  observation/
  extraction/
  actions/
  vision/
  screen/
  schemas/
  utils/

==================================================
CANONICAL SCHEMAS TO CREATE FIRST
==================================================

Create these canonical models first and use them consistently everywhere:

1. Control
2. ScreenObservation
3. ActionRequest
4. ActionResult
5. BusinessExtraction
6. ValidationResult

These schemas must become the internal language of the system.

==================================================
PHASE-BY-PHASE EXECUTION PLAN
==================================================

PHASE 0 — Current State Review
------------------------------
Goal:
Understand the current codebase before changing anything.

Tasks:
- inspect folder structure
- identify current MCP entrypoints
- identify runtime/session logic
- identify SAP scripting integration points
- identify current command handlers
- identify screenshot support if any
- identify code smells:
  - giant handlers
  - mixed responsibilities
  - scattered wait logic
  - repeated COM access patterns
  - untyped dict-heavy payloads
- identify what can be preserved vs rewritten

Deliverables:
- short architecture review
- list of structural problems
- proposed migration path
- no destructive rewrite yet

Commit style:
chore(architecture): review current sap mcp structure and identify migration plan

--------------------------------------------------

PHASE 1 — Create Canonical Schemas and Base Contracts
-----------------------------------------------------
Goal:
Introduce stable internal contracts before deeper refactor.

Tasks:
- create schemas package
- add:
  - control.py
  - observation.py
  - action_request.py
  - action_result.py
  - extraction.py
  - validation.py
- define typed models
- remove ad hoc dict contracts where practical
- keep compatibility shims if needed

Requirements:
- all key fields typed
- clear field names
- docstrings on models
- comments on important semantics
- avoid over-design

Deliverables:
- canonical schemas in place
- existing code can gradually migrate to them

Commit style:
feat(schemas): introduce canonical sap mcp contracts

--------------------------------------------------

PHASE 2 — Extract Runtime Layer
-------------------------------
Goal:
Separate SAP session/runtime concerns from tool handlers.

Tasks:
- create runtime package
- implement:
  - sap_runtime.py
  - session_manager.py
  - connection_manager.py if needed
  - com_executor.py
  - busy_guard.py
  - modal_guard.py
  - focus_guard.py
  - timeout_policy.py
- move COM attach/session discovery here
- centralize idle waiting
- centralize modal detection
- centralize safe COM execution

Requirements:
- tool handlers should stop talking directly to COM where possible
- runtime should expose clean service methods
- add structured logging for runtime operations

Deliverables:
- runtime layer separated
- session handling no longer mixed with business/tool code

Commit style:
refactor(runtime): isolate sap session and com execution layer

--------------------------------------------------

PHASE 3 — Build Observation Pipeline
------------------------------------
Goal:
Make observation the core foundation.

Tasks:
- create observation package
- implement:
  - raw_snapshot_builder.py
  - normalized_snapshot_builder.py
  - screen_observation_builder.py
  - observation_diff.py
- create ObservationService if helpful
- build get_current_observation flow end-to-end
- include:
  - session info
  - transaction
  - title
  - focused control if possible
  - status bar
  - modal summary
  - normalized controls
  - table/grid/tree summaries
  - screenshot ref placeholder if screenshot not yet ready

Requirements:
- observation must return ScreenObservation
- use canonical schemas
- keep separation between raw extraction and normalization

Deliverables:
- reliable current observation flow

Commit style:
feat(observation): add structured screen observation pipeline

--------------------------------------------------

PHASE 4 — Implement Control Registry and Core Handlers
------------------------------------------------------
Goal:
Introduce component-based control handling.

Tasks:
- create controls package
- implement:
  - control_registry.py
  - base_handler.py
  - field_handler.py
  - button_handler.py
  - tab_handler.py
  - menu_handler.py
  - toolbar_handler.py
  - modal_handler.py
- map SAP GUI scripting control classes to handlers
- each handler should support:
  - identify
  - extract
  - supported actions
  - basic validation

Requirements:
- no giant if/else dispatch blocks
- registry-based lookup
- readable handler boundaries

Deliverables:
- modular control handler system for common controls

Commit style:
feat(controls): add control registry and core sap control handlers

--------------------------------------------------

PHASE 5 — Add Structured Data Control Support
---------------------------------------------
Goal:
Handle heavy SAP data controls properly.

Tasks:
- implement:
  - table_handler.py
  - grid_handler.py
  - tree_handler.py
  - shell_handler.py
- use SAP scripting API PDF carefully
- support shell containers by enumerating/delegating child controls
- support table and grid extraction primitives
- support tree node traversal primitives

Requirements:
- visible rows extraction
- row finding helpers
- selection helpers
- metadata extraction
- guardrails for unsupported variants

Deliverables:
- SAP structured data control support

Commit style:
feat(controls): implement table grid tree and shell handlers

--------------------------------------------------

PHASE 6 — Add Extraction Layer
------------------------------
Goal:
Separate screen observation from business-oriented extraction.

Tasks:
- create extraction package
- implement:
  - form_extractor.py
  - table_extractor.py
  - grid_extractor.py
  - tree_extractor.py
  - entity_extractor.py
  - semantic_enricher.py
  - validation_engine.py
- support:
  - form extraction
  - visible sections
  - field-label mapping
  - row extraction
  - semantic enrichment
  - validation/confidence

Requirements:
- extraction must build on normalized controls
- include completeness and confidence
- no LLM reasoning here

Deliverables:
- reusable extraction pipeline

Commit style:
feat(extraction): add structured extraction and validation pipeline

--------------------------------------------------

PHASE 7 — Implement Screenshot/Vision Support
---------------------------------------------
Goal:
Make screenshot capture a first-class runtime feature.

Tasks:
- create vision package
- implement:
  - screenshot_service.py
  - region_cropper.py
  - screenshot_diff.py
- capture active SAP window screenshot
- return screenshot refs in observations and action results
- support optional region capture for modal/status/table focus

Requirements:
- runtime-safe screenshot capture
- file naming stable and traceable
- no screenshot reasoning inside MCP

Deliverables:
- screenshot capture and diff support

Commit style:
feat(vision): add sap screenshot capture and diff support

--------------------------------------------------

PHASE 8 — Implement Action Execution Pipeline
---------------------------------------------
Goal:
Create one deterministic path for all actions.

Tasks:
- create actions package
- implement:
  - action_executor.py
  - action_validator.py
  - action_verifier.py
  - navigation_actions.py
  - field_actions.py
  - table_actions.py
  - grid_actions.py
  - tree_actions.py
  - modal_actions.py
- every action must follow:
  1 validate request
  2 resolve target
  3 wait for idle
  4 execute
  5 wait for settle
  6 capture new observation
  7 verify expected result
  8 return ActionResult

Requirements:
- no direct ad hoc actions outside executor
- verification included
- warnings included
- new observation returned

Deliverables:
- deterministic action execution pipeline

Commit style:
feat(actions): add deterministic sap action execution pipeline

--------------------------------------------------

PHASE 9 — Expose Proper MCP Tool Surface
----------------------------------------
Goal:
Refactor MCP server interface around capabilities.

Tasks:
- refactor server package
- implement/clean:
  - mcp_server.py
  - tool_router.py
  - request_context.py
- expose tools such as:
  - list_sessions
  - attach_session
  - get_current_observation
  - capture_screenshot
  - navigate_tcode
  - set_field
  - get_field
  - press_button
  - send_vkey
  - select_tab
  - select_menu_path
  - get_table_rows
  - find_table_rows
  - get_grid_rows
  - find_grid_rows
  - select_tree_node
  - confirm_modal
  - cancel_modal
- normalize request/response format

Requirements:
- no flow-specific tools
- capability-first naming
- clean routing
- consistent error handling

Deliverables:
- production-like MCP tool surface

Commit style:
refactor(server): expose capability-based sap mcp tool surface

--------------------------------------------------

PHASE 10 — Add Screen Classification Support
--------------------------------------------
Goal:
Provide planner-support metadata without domain hardcoding.

Tasks:
- create screen package
- implement:
  - screen_classifier.py
  - screen_registry.py
- support:
  - generic form screen
  - generic table screen
  - generic grid screen
  - generic modal screen
- optionally leave extension points for future domain screens

Requirements:
- this is helper metadata, not domain workflow logic
- keep it lightweight

Deliverables:
- screen classification helpers for agents

Commit style:
feat(screen): add generic sap screen classification helpers

--------------------------------------------------

PHASE 11 — Cleanup, Documentation, and Migration Notes
------------------------------------------------------
Goal:
Make the repo easy to extend and open-source quality.

Tasks:
- remove stale code paths where safe
- add module-level docstrings
- improve README or docs references
- add migration notes
- ensure comments are useful and not noisy
- ensure naming is consistent
- ensure architecture matches docs

Deliverables:
- clean repo
- understandable modules
- clear extension points
- summary of what remains

Commit style:
docs(architecture): align implementation with sap mcp design spec

==================================================
MCP CAPABILITIES THAT MUST EXIST BY END
==================================================

Observation
- list_sessions
- attach_session
- get_current_observation
- get_visible_controls
- get_status_bar
- get_active_modal
- capture_screenshot
- diff_last_observation

Actions
- navigate_tcode
- set_field
- get_field
- clear_field
- press_button
- send_vkey
- select_tab
- select_menu_path
- select_table_row
- double_click_grid_row
- expand_tree_node
- collapse_tree_node
- select_tree_node
- confirm_modal
- cancel_modal

Extraction
- extract_form
- get_table_rows
- find_table_rows
- get_grid_rows
- find_grid_rows
- get_tree_nodes
- extract_business_entities

Verification
- wait_for_idle
- verify_expected_state
- wait_for_screen_change

==================================================
SAP CONTROL SUPPORT REQUIREMENTS
==================================================

Must support these SAP GUI scripting control families where available:

Fields
- GuiTextField
- GuiCTextField
- GuiPasswordField
- GuiComboBox
- GuiCheckBox
- GuiRadioButton

Buttons / Nav
- GuiButton
- toolbar buttons
- menus
- tabs

Structured Controls
- GuiTableControl
- GuiGridView / ALV
- GuiTree
- shell/container-based controls

Windows / Messaging
- main window
- modal window
- status bar
- labels

For table/grid/tree/shell:
- implement appropriate specialized logic, not generic fake handling

==================================================
COMMENTING / DOCSTRING REQUIREMENTS
==================================================

Code must be well documented.

Add:
- docstrings for all public classes
- docstrings for public methods
- concise comments for tricky SAP-specific behavior
- comments for retry/wait decisions where non-obvious
- extension notes where future SAP variants are likely

Do NOT add noisy comments explaining obvious Python syntax.

==================================================
OUTPUT FORMAT FOR EACH PHASE
==================================================

For each phase you complete, respond with:

1. Summary
2. Files added
3. Files modified
4. Architectural reasoning
5. Known limitations
6. Next phase recommendation

When changing code, prefer complete, production-quality implementation over placeholder pseudo-code.

If current code is poor quality:
- replace it carefully
- preserve behavior where useful
- improve readability, naming, and modularity

If some SAP GUI scripting variant is ambiguous:
- implement the cleanest extensible abstraction
- leave a clearly documented TODO with rationale

==================================================
FINAL EXPECTATION
==================================================

By the end, the repo should become a clean, extensible SAP MCP runtime that:
- is deterministic
- is capability-based
- is suitable for AI agents
- is screenshot-aware
- handles SAP controls properly
- follows open-source architecture standards
- is far better than the current debug-flow-specific implementation

Start with Phase 0 review of the existing codebase, then proceed phase by phase.
Do not skip architecture discipline.
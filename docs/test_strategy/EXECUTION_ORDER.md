# SAP MCP Testing Execution Order

Follow this sequence to verify the new SAP MCP server implementation. This order ensures that foundational requirements (Environment) are met before progressing to complex behavioral tests.

## 1. Environment Readiness
**File**: [WINDOWS_VM_ENVIRONMENT_CHECKLIST.md](file:///Users/girish/girish-workspace/SapAdapter.Python/docs/test_strategy/WINDOWS_VM_ENVIRONMENT_CHECKLIST.md)
- **Goal**: Ensure the Windows machine has SAP GUI installed, "Scripting" enabled, and the correct Python version.
- **Why**: Without this, the COM layers will fail to initialize.

## 2. Manual Component Verification
**File**: [MCP_MANUAL_TEST_PLAN.md](file:///Users/girish/girish-workspace/SapAdapter.Python/docs/test_strategy/MCP_MANUAL_TEST_PLAN.md)
- **Goal**: Start the server and perform basic connectivity checks (Health, List Sessions).
- **Why**: Confirms that the server can actually reach the SAP subsystems.

## 3. Automated Protocol Suite
**File**: [MCP_AUTOMATED_TEST_PLAN.md](file:///Users/girish/girish-workspace/SapAdapter.Python/docs/test_strategy/MCP_AUTOMATED_TEST_PLAN.md)
- **Goal**: Run the structured Python test suite to verify individual tools (Observe, Execute).
- **Why**: Provides deterministic validation of action execution and wait strategies.

## 4. Agentic Validation
**File**: [AGENT_VALIDATION_PROMPTS.md](file:///Users/girish/girish-workspace/SapAdapter.Python/docs/test_strategy/AGENT_VALIDATION_PROMPTS.md)
- **Goal**: Connect a real AI agent (running the MCP client) and use the provided prompts to navigate SAP.
- **Why**: Final end-to-end verification of the "AI-Ready" claim.

## 5. Success Sign-off
**File**: [SUCCESS_CRITERIA.md](file:///Users/girish/girish-workspace/SapAdapter.Python/docs/test_strategy/SUCCESS_CRITERIA.md)
- **Goal**: Cross-reference results with the defined project goals.
- **Artifact**: Use [MCP_VALIDATION_REPORT_TEMPLATE.md](file:///Users/girish/girish-workspace/SapAdapter.Python/docs/test_strategy/MCP_VALIDATION_REPORT_TEMPLATE.md) to document the results.

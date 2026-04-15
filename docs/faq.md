# Frequently Asked Questions (FAQ)

## 1. Does this work on Mac or Linux?
No. The adapter relies on SAP GUI for Windows COM automation technology, which is exclusive to the Windows operating system.

## 2. Does this support SAP Fiori or WebGUI?
Not directly. This adapter is specifically for the SAP GUI for Windows client. For Fiori/WebGUI, you might want to use a Playwright-based MCP server. However, many Fiori apps can be opened in SAP GUI if they have a corresponding transaction code.

## 3. Can I run this without SAP GUI being open?
No. The adapter attaches to an active SAP GUI process. It does not perform headless background RFC or OData calls.

## 4. Is it safe to use LLMs with my production SAP system?
You should exercise caution. While the adapter provides "safety guards" (like `BusyGuard`), the **logic** of what to do is determined by the AI agent. We strongly recommend testing all automation in a sandbox environment and implementing human-in-the-loop verification for critical transactions.

## 5. How do I handle ALV Grids or complex tables?
The adapter includes specialized handlers for `GuiGridView` and `GuiTableControl`. Use `sap_observe_screen` to get a summary of the grid, and `sap_table_action` or `sap_execute_action` with `cell` coordinates to interact with them.

## 6. The agent keeps saying "I can't find the button". What should I do?
1. Ensure the screen is actually loaded.
2. Check if a modal dialog is blocking the interaction (use `sap_observe_screen` to check for `isModal`).
3. Ensure the `target_id` is correct. You may need to "refresh" the observation if the screen has changed.

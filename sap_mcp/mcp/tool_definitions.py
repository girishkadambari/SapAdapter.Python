from typing import List, Dict, Any

def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Returns the standard MCP tool definitions for the SAP MCP server.
    """
    return [
        {
            "name": "list_sessions",
            "description": (
                "PURPOSE: Discovery of active SAP GUI windows.\n"
                "WHEN TO USE: Always call this first when starting a session to identify connection and session indices. "
                "The resulting 'sessionId' (e.g. '0-0') must be passed to all subsequent calls."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_screen_summary",
            "description": (
                "PURPOSE: Fast high-level understanding of the current screen.\n"
                "WHEN TO USE: Always use this as the default observation tool. "
                "It returns window metadata, status bar info, and only 'high-value' controls (editable fields and primary buttons). "
                "This significantly reduces token usage compared to a full screen dump."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string", "description": "The SAP session identifier." }
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "inspect_control",
            "description": (
                "PURPOSE: Detailed property extraction for a specific control.\n"
                "WHEN TO USE: Call this when you have a target_id from the summary and need full details (e.g. table column structure, tooltips, or exact bounds)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" },
                    "target_id": { "type": "string", "description": "The absolute SAP ID of the control." }
                },
                "required": ["session_id", "target_id"]
            }
        },
        {
            "name": "capture_visual",
            "description": (
                "PURPOSE: Visual verification without payload bloat.\n"
                "WHEN TO USE: Use for debugging or verifying complex layouts. "
                "Saves a screenshot to a local path and returns the path + bounding boxes of visible controls. "
                "DOES NOT return base64 data directly to avoid token overflow."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" },
                    "save_path": { "type": "string", "description": "Optional absolute path to save the image. If not provided, a default temporary path is used." }
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "observe_screen",
            "description": (
                "DEPRECATED: Use 'get_screen_summary' instead for better performance.\n"
                "PURPOSE: Full UI state dump including recursive scan."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" },
                    "include_screenshot": { "type": "boolean", "default": False }
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "sap_navigate",
            "description": (
                "PURPOSE: Fast traversal via Transaction Codes or keyboard emulation.\n"
                "WHEN TO USE: Use 'navigate_tcode' for global navigation (e.g. '/nME21N'). "
                "Use 'send_vkey' for keyboard shortcuts: 0 (Enter), 3 (Back), 11 (Save), 12 (Cancel)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" },
                    "action_type": { "type": "string", "enum": ["navigate_tcode", "send_vkey"] },
                    "tcode": { "type": "string", "description": "The T-Code (e.g. VA01). Start with /n to clear current transaction." },
                    "vkey": { "type": "integer", "description": "The SAP Virtual Key code." }
                },
                "required": ["session_id", "action_type"]
            }
        },
        {
            "name": "sap_interact_field",
            "description": (
                "PURPOSE: Atomic UI interactions with standard controls.\n"
                "WHEN TO USE: Use for GuiTextField, GuiComboBox, GuiCheckBox, and GuiTab. "
                "For ComboBoxes (dropdowns), provide the internal 'Key' value. "
                "For Tabs, set action_type to 'select_tab'. "
                "This is the primary tool for filling forms."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" },
                    "target_id": { "type": "string", "description": "The absolute SAP ID (e.g. wnd[0]/usr/txt...). Use the ID provided in 'observe_screen'." },
                    "action_type": { "type": "string", "enum": ["set_field", "set_checkbox", "select_tab"] },
                    "value": { "type": "string", "description": "The input text, boolean checkbox state, or dropdown key." }
                },
                "required": ["session_id", "target_id", "action_type"]
            }
        },
        {
            "name": "sap_table_action",
            "description": (
                "PURPOSE: High-level interaction with GuiTableControl and ALV GridView components.\n"
                "WHEN TO USE: Mandatory for any control of type 'table' or 'grid' identified in observation. "
                "Supports numeric column indices (e.g. 5) or logical SAP names (e.g. 'MEPO1211-EMATN'). "
                "Performs a verified write (read-back) to ensure the value was applied."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" },
                    "target_id": { "type": "string" },
                    "action_type": { "type": "string", "enum": ["set_cell_data", "get_cell_data", "activate_cell", "select_row", "find_row_by_text", "table_batch_fill"] },
                    "row": { "type": "integer", "description": "Logical row index starting from 0." },
                    "column": { "type": "string", "description": "The technical column name or numeric index." },
                    "value": { "type": "string", "description": "Input value or search criterion." },
                    "rows": { 
                        "type": "array", 
                        "description": "Used only for table_batch_fill. List of {row, data: {col: val}} objects.",
                        "items": { "type": "object" }
                    }
                },
                "required": ["session_id", "target_id", "action_type"]
            }
        },
        {
            "name": "sap_tree_action",
            "description": (
                "PURPOSE: Navigating hierarchical SAP Trees.\n"
                "WHEN TO USE: Use for 'GuiTree' controls. "
                "Action 'expand_node' reveals children. "
                "Action 'select_node' focuses a specific branch. "
                "Always use the 'node_key' provided in the observation metadata."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" },
                    "target_id": { "type": "string" },
                    "action_type": { "type": "string", "enum": ["select_node", "expand_node", "double_click_node"] },
                    "node_key": { "type": "string", "description": "Internal SAP node identifier." }
                },
                "required": ["session_id", "target_id", "action_type", "node_key"]
            }
        },
        {
            "name": "sap_shell_action",
            "description": (
                "PURPOSE: Executing actions on specialized GuiShell subtypes like Toolbars or Pictures.\n"
                "WHEN TO USE: Use for 'toolbar' controls or generic 'shell' components. "
                "Action 'press_button' is used for clicking icons in the application toolbar. "
                "Provide the 'button_id' or tooltip found in the control's metadata."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" },
                    "target_id": { "type": "string" },
                    "action_type": { "type": "string", "enum": ["press_button", "click"] },
                    "button_id": { "type": "string", "description": "Technical ID or tooltip text." }
                },
                "required": ["session_id", "target_id", "action_type"]
            }
        },
        {
            "name": "execute_batch",
            "description": (
                "PURPOSE: Atomic execution of multiple actions in a single request.\n"
                "WHEN TO USE: Use to perform a sequence of safe interactions (e.g. filling multiple fields in a form) without multi-turn latency. "
                "Returns a list of structured results for each action. "
                "The server will stop and return if a critical error occurs, reporting the exact failure step."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" },
                    "actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "tool": { "type": "string", "enum": ["sap_interact_field", "sap_navigate", "sap_table_action", "sap_tree_action", "sap_shell_action"] },
                                "action_type": { "type": "string" },
                                "target_id": { "type": "string" },
                                "params": { "type": "object", "additionalProperties": True },
                                "row": { "type": "integer" },
                                "column": { "type": "string" },
                                "value": { "type": "string" }
                            },
                            "required": ["tool", "action_type"]
                        }
                    }
                },
                "required": ["session_id", "actions"]
            }
        },
        {
            "name": "interaction_search_help_select",
            "description": (
                "PURPOSE: Semantic selection from an SAP Search Help (F4) hit list.\n"
                "WHEN TO USE: Use this after a search help hit-list appears. "
                "It automatically detects if the list is a modern GridView or a legacy amodal list. "
                "It attempts to select the row and confirm the selection."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" },
                    "row": { "type": "integer", "description": "The row index to select (starting from 0).", "default": 0 },
                    "value": { "type": "string", "description": "Optional: Match the row by text value." }
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "get_sap_context",
            "description": (
                "PURPOSE: Fast retrieval of current SAP session context.\n"
                "WHEN TO USE: Use to verify the current transaction, program, dynpro, and status bar without a full screen dump."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" }
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "get_status_and_incompletion",
            "description": (
                "PURPOSE: Comprehensive check of document status and incompletion logs.\n"
                "WHEN TO USE: Use before saving a document to ensure no blocking errors exist."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": { "type": "string" }
                },
                "required": ["session_id"]
            }
        }
    ]


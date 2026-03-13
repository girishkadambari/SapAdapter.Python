from typing import List, Dict, Any

def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Returns the standard MCP tool definitions for the SAP MCP server.
    """
    return [
        {
            "name": "list_sessions",
            "description": "Discover all active SAP GUI sessions on the local machine.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "observe_screen",
            "description": "Capture a structured observation of the current SAP screen, including all controls, status bar, and active modals.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Optional ID of the session to observe. If omitted, the active session is used."
                    },
                    "include_screenshot": {
                        "type": "boolean",
                        "description": "Whether to include a base64-encoded screenshot in the response.",
                        "default": False
                    }
                },
                "required": []
            }
        },
        {
            "name": "execute_action",
            "description": "Execute a deterministic action on a specific SAP control.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The ID of the session where the action should be executed."
                    },
                    "target_id": {
                        "type": "string",
                        "description": "The SAP GUI ID of the target control (e.g., wnd[0]/usr/btn[0])."
                    },
                    "action_type": {
                        "type": "string",
                        "enum": ["set_text", "press", "select", "set_value"],
                        "description": "The type of action to execute."
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameters for the action (e.g., {'value': 'new text'})."
                    }
                },
                "required": ["session_id", "target_id", "action_type"]
            }
        },
        {
            "name": "extract_entity",
            "description": "Extract a high-level business entity (e.g., SalesOrder, Customer) from the current screen.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The ID of the session to extract from."
                    },
                    "entity_type": {
                        "type": "string",
                        "description": "The type of entity to extract (e.g., 'SalesOrder')."
                    }
                },
                "required": ["session_id", "entity_type"]
            }
        }
    ]

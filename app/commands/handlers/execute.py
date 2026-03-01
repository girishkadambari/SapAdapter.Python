# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/commands/handlers/execute.py
from loguru import logger
from .navigation import navigate_tcode, read_field, focus_field
from .modification import set_field, press_toolbar_button
from .grid import get_grid_summary, get_grid_rows, find_grid_rows
from .table import get_table_summary, get_table_rows, find_table_rows
from .tree import get_tree_nodes, find_tree_nodes, select_tree_node
from .menu import get_menu_paths, select_menu_path
from .otc import (
    get_sales_order, check_credit_limit, get_receivables, 
    navigate_credit_release, release_credit_block, 
    open_po_display, open_po_history
)

# This map routes SapCommand types to their specific implementation functions
_COMMAND_MAP = {
    # Navigation & Basic
    "navigateTcode": navigate_tcode,
    "readField": read_field,
    "focusField": focus_field,
    "setField": set_field,
    "pressToolbarButton": press_toolbar_button,
    
    # Grid (ALV)
    "GRID_GET_SUMMARY": get_grid_summary,
    "GRID_GET_ROWS": get_grid_rows,
    "GRID_FIND_ROWS": find_grid_rows,
    
    # Table Control
    "TABLE_GET_SUMMARY": get_table_summary,
    "TABLE_GET_ROWS": get_table_rows,
    "TABLE_FIND_ROWS": find_table_rows,
    
    # Tree Control
    "TREE_GET_VISIBLE_NODES": get_tree_nodes,
    "TREE_FIND_NODES": find_tree_nodes,
    "TREE_SELECT_NODE": select_tree_node,
    
    # Menu Bar
    "MENU_GET_PATHS": get_menu_paths,
    "MENU_SELECT_PATH": select_menu_path,
    
    # OTC Workflows (Agent Actions)
    "GET_SALES_ORDER": get_sales_order,
    "CHECK_CREDIT_LIMIT": check_credit_limit,
    "GET_RECEIVABLES": get_receivables,
    "NAVIGATE_CREDIT_RELEASE": navigate_credit_release,
    "RELEASE_CREDIT_BLOCK": release_credit_block,
    "OPEN_PO_DISPLAY": open_po_display,
    "OPEN_PO_HISTORY": open_po_history,
}

async def execute_command(session, payload):
    """
    Dispatcher for 'executeCommand' request type.
    Payload is expected to be a SapCommand object.
    """
    cmd_type = payload.get("type")
    cmd_payload = payload.get("payload", {})
    cmd_id = payload.get("id", "unknown")
    
    logger.info(f"Dispatching SapCommand: {cmd_type} (id: {cmd_id})")
    
    # Modal Check
    try:
        if session.Info.Status == 1:
            logger.warning("Modal dialog detected. Blocking command execution.")
            raise ValueError("MODAL_DETECTED: A modal dialog is open in SAP. Please close it first.")
    except Exception as e:
        if "MODAL_DETECTED" in str(e): raise
        logger.debug(f"Modal check failed (could be transient): {str(e)}")

    if cmd_type not in _COMMAND_MAP:
        logger.warning(f"Unsupported SapCommand type: {cmd_type}")
        raise ValueError(f"Unsupported SapCommand type: {cmd_type}")
        
    handler = _COMMAND_MAP[cmd_type]
    return await handler(session, cmd_payload)

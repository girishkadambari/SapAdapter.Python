import os
from pathlib import Path
from typing import Dict, Any, List, Set
from enum import Enum

class ScreenType(str, Enum):
    SEARCH_INPUT = "SEARCH_INPUT"       # Initial screen for searching/selecting records
    DETAIL_VIEW = "DETAIL_VIEW"         # Display/Edit view of a specific record
    GRID_LIST = "GRID_LIST"             # ALV Grid or Table-heavy list
    DASHBOARD = "DASHBOARD"           # Main menu or overview screen with many icons/tiles
    MENU_TREE = "MENU_TREE"           # Easy Access menu or similar tree structure
    POPUP_DIALOG = "POPUP_DIALOG"     # Small modal dialogs
    UNKNOWN = "UNKNOWN"

class Config:
    """
    Centralized configuration for the SAP MCP Server.
    """
    # Project Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    TEMP_DIR = Path(os.environ.get("TEMP", "/tmp"))
    
    # SAP GUI Constants
    DEFAULT_VKEY_ENTER = 0
    DEFAULT_VKEY_BACK = 3
    DEFAULT_VKEY_SAVE = 11
    DEFAULT_VKEY_CANCEL = 12
    
    # Observation Settings
    MAX_RECURSION_DEPTH = 100
    SCREENSHOT_QUALITY = 80
    
    # Tool Naming Conventions
    TOOL_PREFIX = "sap_"
    
    SCREEN_SIGNATURES = {
        ScreenType.SEARCH_INPUT: {
            "required_types": {"GuiCTextField", "GuiButton"},
            "preferred_labels": {"Search", "Execute", "Find", "Selection"},
            "max_tables": 0
        },
        ScreenType.DETAIL_VIEW: {
            "required_types": {"GuiTextField", "GuiLabel"},
            "preferred_labels": {"Display", "Change", "General Data", "Header"},
            "min_controls": 20
        },
        ScreenType.GRID_LIST: {
            "required_types": {"GuiGridView", "GuiShell"},
            "min_tables": 1
        },
        ScreenType.MENU_TREE: {
            "required_types": {"GuiTree"}
        },
        ScreenType.DASHBOARD: {
            "required_types": {"GuiImage", "GuiButton"},
            "max_text_fields": 5
        }
    }

    @classmethod
    def get_screenshot_path(cls, filename: str) -> str:
        return str(cls.TEMP_DIR / filename)

# Action Types as constants for predictability
class ActionTypes:
    SET_FIELD = "set_field"
    SET_CHECKBOX = "set_checkbox"
    SELECT_RADIO = "select_radio"
    PRESS_BUTTON = "press_button"
    SELECT_TAB = "select_tab"
    NAVIGATE_TCODE = "navigate_tcode"
    SEND_VKEY = "send_vkey"
    SET_CELL_DATA = "set_cell_data"
    GET_CELL_DATA = "get_cell_data"
    SELECT_ROW = "select_row"
    FIND_ROW_BY_TEXT = "find_row_by_text"
    TABLE_BATCH_FILL = "table_batch_fill"
    SEARCH_HELP_SELECT = "search_help_select"
    
    # Shell specific
    SELECT_NODE = "select_node"
    EXPAND_NODE = "expand_node"
    COLLAPSE_NODE = "collapse_node"
    DOUBLE_CLICK_NODE = "double_click_node"
    FIND_NODE_BY_PATH = "find_node_by_path"
    PRESS_CONTEXT_BUTTON = "press_context_button"
    SELECT_MENU_ITEM = "select_menu_item"
    ACTIVATE_CELL = "activate_cell"
    CLICK = "click"

class SapGuiTypes:
    TEXT_FIELD = "GuiTextField"
    C_TEXT_FIELD = "GuiCTextField"
    PASSWORD_FIELD = "GuiPasswordField"
    LABEL = "GuiLabel"
    BUTTON = "GuiButton"
    CHECKBOX = "GuiCheckBox"
    RADIO_BUTTON = "GuiRadioButton"
    COMBOBOX = "GuiComboBox"
    TAB = "GuiTab"
    MENU = "GuiMenu"
    MENU_BAR = "GuiMenuBar"
    TOOLBAR = "GuiToolbar"
    STATUSBAR = "GuiStatusbar"
    TABLE_CONTROL = "GuiTableControl"
    GRID_VIEW = "GuiGridView"
    TREE = "GuiTree"
    SHELL = "GuiShell"
    IMAGE = "GuiImage"
    MODAL_WINDOW = "GuiModalWindow"
    CONTAINER_SHELL = "GuiContainerShell"

class StatusBarTypes:
    SUCCESS = "S"
    ERROR = "E"
    WARNING = "W"
    INFO = "I"
    ABORT = "A"

class ControlSubtypes:
    BUTTON = "button"
    TEXT = "text"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    COMBOBOX = "combobox"
    TABLE = "table"
    GRID = "grid"
    TREE = "tree"
    TAB = "tab"
    MENU = "menu"
    STATUSBAR = "statusbar"
    LABEL = "label"
    IMAGE = "image"
    PASSWORD = "password"
    DIALOG = "dialog"
    UNKNOWN = "unknown"

class ShellSubtypes:
    TREE = "Tree"
    TOOLBAR = "Toolbar"
    GRID_VIEW = "GridView"
    PICTURE = "Picture"
    HTML_VIEW = "HtmlViewer"
    CALENDAR = "Calendar"
    TEXT_EDIT = "TextEdit"

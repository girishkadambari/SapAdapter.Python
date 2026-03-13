from enum import Enum
from typing import List, Dict, Set

class ScreenType(str, Enum):
    SEARCH_INPUT = "SEARCH_INPUT"       # Initial screen for searching/selecting records
    DETAIL_VIEW = "DETAIL_VIEW"         # Display/Edit view of a specific record
    GRID_LIST = "GRID_LIST"             # ALV Grid or Table-heavy list
    DASHBOARD = "DASHBOARD"           # Main menu or overview screen with many icons/tiles
    MENU_TREE = "MENU_TREE"           # Easy Access menu or similar tree structure
    POPUP_DIALOG = "POPUP_DIALOG"     # Small modal dialogs
    UNKNOWN = "UNKNOWN"

SIGNATURES = {
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

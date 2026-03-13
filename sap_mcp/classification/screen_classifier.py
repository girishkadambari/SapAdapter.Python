from typing import List, Dict, Any
from loguru import logger
from ..schemas.observation import ScreenObservation
from ..schemas.control import Control
from .patterns import ScreenType, SIGNATURES

class ScreenClassifier:
    """
    Engine for identifying the functional type of a SAP screen.
    """
    
    def classify(self, controls: List[Control], title: str) -> ScreenType:
        """
        Analyzes the set of controls and window title to determine the screen type.
        """
        if not controls:
            return ScreenType.UNKNOWN
            
        # 1. Gather statistics
        control_types = {c.type for c in controls}
        control_count = len(controls)
        table_count = sum(1 for c in controls if c.type in {"GuiTableControl", "GuiGridView", "GuiShell"})
        text_field_count = sum(1 for c in controls if c.type in {"GuiTextField", "GuiCTextField"})
        
        title_upper = title.upper()
        
        # 2. Heuristic Matching
        
        # Grid List is usually very distinct
        if "GuiGridView" in control_types or ("GuiTableControl" in control_types and control_count < 50):
            return ScreenType.GRID_LIST
            
        # Menu Tree (Easy Access)
        if "GuiTree" in control_types:
            return ScreenType.MENU_TREE
            
        # Search Input
        if any(kw in title_upper for kw in ["SEARCH", "SELECT", "FIND", "INITIAL"]):
            if text_field_count > 0 and text_field_count < 15:
                return ScreenType.SEARCH_INPUT
                
        # Detail View
        if any(kw in title_upper for kw in ["DISPLAY", "CHANGE", "CREATE", "HEADER"]):
            if control_count > 15:
                return ScreenType.DETAIL_VIEW
                
        # Dashboard/Home
        if "GuiImage" in control_types and text_field_count < 5:
            return ScreenType.DASHBOARD

        # 3. Fallback to signatures
        for s_type, sig in SIGNATURES.items():
            req_types = sig.get("required_types", set())
            if req_types and req_types.issubset(control_types):
                return s_type
                
        return ScreenType.UNKNOWN

    def get_metadata(self, controls: List[Control], screen_type: ScreenType) -> Dict[str, Any]:
        """
        Extracts additional context metadata based on the classified screen type.
        """
        metadata = {
            "control_count": len(controls),
            "has_errors": any("error" in (c.label or "").lower() for c in controls if c.type == "GuiLabel")
        }
        
        if screen_type == ScreenType.GRID_LIST:
            metadata["grid_count"] = sum(1 for c in controls if c.type == "GuiGridView")
            
        return metadata

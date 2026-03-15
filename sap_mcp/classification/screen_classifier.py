from typing import List, Dict, Any
from loguru import logger
from ..schemas.observation import ScreenObservation
from ..schemas.control import Control
from ..core.config import Config, ScreenType

class ScreenClassifier:
    """
    Engine for identifying the functional type of a SAP screen.
    Now strictly data-driven via Config.SCREEN_SIGNATURES.
    """
    
    def classify(self, controls: List[Control], title: str) -> ScreenType:
        """
        Analyzes the set of controls and window title to determine the screen type.
        """
        if not controls:
            return ScreenType.UNKNOWN
            
        control_types = {c.type for c in controls}
        title_upper = title.upper()
        
        # 1. Signature-based Matching (Reliable)
        for s_type, sig in Config.SCREEN_SIGNATURES.items():
            req_types = sig.get("required_types", set())
            if req_types and req_types.issubset(control_types):
                # Additional title check if provided
                pref_labels = sig.get("preferred_labels", set())
                if not pref_labels or any(lab.upper() in title_upper for lab in pref_labels):
                    return s_type
        
        # 2. Heuristic Heuristics (Fallback)
        if SapGuiTypes.GRID_VIEW in control_types:
            return ScreenType.GRID_LIST
        if SapGuiTypes.TREE in control_types:
            return ScreenType.MENU_TREE
            
        if any(kw in title_upper for kw in ["DISPLAY", "CHANGE", "CREATE"]):
            return ScreenType.DETAIL_VIEW
                
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

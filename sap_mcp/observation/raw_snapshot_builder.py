import json
from typing import Any, Dict, List, Optional
from loguru import logger

class RawSnapshotBuilder:
    """
    Optimized extractor that captures raw SAP GUI control properties using GetObjectTree.
    """
    
    def get_raw_snapshot(self, session: Any) -> Dict[str, Any]:
        """
        Captures a raw snapshot of the SAP GUI session using GetObjectTree optimization.
        """
        if not hasattr(session, "GetObjectTree"):
            raise RuntimeError("GetObjectTree is not supported on this SAP version. Please upgrade to SAP 7.70 or higher.")

        return self._capture_optimized(session)

    def _capture_optimized(self, session: Any) -> Dict[str, Any]:
        """Uses GetObjectTree to fetch the UI hierarchy in a single batch call."""
        # Request common properties for all elements
        props = ["Id", "Type", "Text", "Tooltip", "Visible", "Changeable", "Left", "Top", "Width", "Height", "SubType"]
        
        try:
            # GetObjectTree returns a JSON string
            json_str = session.GetObjectTree("", props)
            tree = json.loads(json_str)
            return {"optimized_tree": tree, "is_optimized": True}
        except Exception as e:
            logger.error(f"GetObjectTree extraction failed: {str(e)}")
            raise

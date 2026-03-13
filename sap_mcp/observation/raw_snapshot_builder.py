from typing import Any, Dict, List, Optional
from loguru import logger

class RawSnapshotBuilder:
    """
    Primitive extractor that captures raw SAP GUI control properties.
    """
    
    def capture(self, container: Any) -> List[Dict[str, Any]]:
        """
        Recursively captures all children of a container.
        """
        raw_controls = []
        self._collect_recursive(container, raw_controls)
        return raw_controls

    def _collect_recursive(self, container: Any, controls: List[Dict[str, Any]]):
        if not container:
            return
            
        try:
            # Capture current control properties
            controls.append(self._extract_properties(container))
            
            # Recurse into children if they exist
            if hasattr(container, "Children"):
                children = container.Children
                for i in range(children.Count):
                    self._collect_recursive(children(i), controls)
        except Exception as e:
            logger.debug(f"Error extracting from container {getattr(container, 'Id', 'unknown')}: {str(e)}")

    def _extract_properties(self, control: Any) -> Dict[str, Any]:
        """
        Extracts all relevant raw properties from a GuiComponent.
        """
        props = {
            "id": str(getattr(control, "Id", "")),
            "type": str(getattr(control, "Type", "")),
            "text": str(getattr(control, "Text", "")) if hasattr(control, "Text") else None,
            "tooltip": str(getattr(control, "Tooltip", "")) if hasattr(control, "Tooltip") else None,
            "changeable": bool(getattr(control, "Changeable", False)),
            "visible": bool(getattr(control, "Visible", True)),
            "parent_id": str(getattr(control, "Parent", {}).Id) if getattr(control, "Parent", None) else None,
        }
        
        # Capture position/size if available
        try:
            if hasattr(control, "Left") and hasattr(control, "Top"):
                props["bounds"] = (
                    int(control.Left),
                    int(control.Top),
                    int(control.Width),
                    int(control.Height)
                )
        except:
            pass
            
        return props

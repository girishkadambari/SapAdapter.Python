import json
from typing import Any, Dict, List, Optional
from loguru import logger

class RawSnapshotBuilder:
    """
    Primitive extractor that captures raw SAP GUI control properties.
    """
    
    def capture(self, container: Any, force_recursive: bool = False) -> List[Dict[str, Any]]:
        """
        Captures all children of a container, using GetObjectTree if available.
        """
        # If we are starting from a Session object, we can use GetObjectTree
        # Check if container is a session or active window
        session = None
        if hasattr(container, "GetObjectTree") and not force_recursive:
            session = container
        elif hasattr(container, "Parent") and hasattr(container.Parent, "GetObjectTree") and not force_recursive:
            # If it's a window, parent might be connection, but we need session.
            # Usually we pass the Session to this builder for tree capture.
            pass

        if session and not force_recursive:
            try:
                return self._capture_via_tree_method(session)
            except Exception as e:
                logger.warning(f"GetObjectTree failed, falling back to recursive: {str(e)}")

        raw_controls = []
        self._collect_recursive(container, raw_controls)
        return raw_controls

    def _capture_via_tree_method(self, session: Any) -> List[Dict[str, Any]]:
        """
        Uses the high-performance GetObjectTree method.
        """
        # Define properties we want to extract
        # Note: Left, Top, Width, Height are often returned as Bounds or individual props
        props = ["Id", "Type", "Text", "Tooltip", "Changeable", "Visible", "Left", "Top", "Width", "Height"]
        
        # Call GetObjectTree
        # Empty string for Id means complete tree
        tree_json_str = session.GetObjectTree("", props)
        if not tree_json_str:
            return []
            
        tree_data = json.loads(tree_json_str)
        
        # The output of GetObjectTree is usually a hierarchical structure
        # We need to flatten it to match the expected List[Dict[str, Any]]
        flat_controls = []
        self._flatten_tree(tree_data, None, flat_controls)
        return flat_controls

    def _flatten_tree(self, node: Dict[str, Any], parent_id: Optional[str], result: List[Dict[str, Any]]):
        """
        Recursively flattens the JSON tree from GetObjectTree.
        """
        # Extract properties with case-insensitive mapping if needed
        # SAP JSON usually uses exact property names passed in
        raw_props = {
            "id": node.get("Id", ""),
            "type": node.get("Type", ""),
            "text": node.get("Text"),
            "tooltip": node.get("Tooltip"),
            "changeable": node.get("Changeable", False),
            "visible": node.get("Visible", True),
            "parent_id": parent_id
        }

        # Handle bounds
        try:
            left = node.get("Left")
            top = node.get("Top")
            width = node.get("Width")
            height = node.get("Height")
            if all(v is not None for v in [left, top, width, height]):
                raw_props["bounds"] = (int(left), int(top), int(width), int(height))
        except:
            pass

        result.append(raw_props)

        # Process children
        children = node.get("Children", [])
        for child in children:
            self._flatten_tree(child, raw_props["id"], result)

    def _collect_recursive(self, container: Any, controls: List[Dict[str, Any]]):
        if not container:
            return
            
        try:
            # Capture current control properties
            controls.append(self._extract_properties(container))
            
            # Recurse into children if they exist
            if hasattr(container, "Children"):
                children = container.Children
                if children is not None:
                    try:
                        count = children.Count
                        for i in range(count):
                            try:
                                child = children(i)
                                if child:
                                    self._collect_recursive(child, controls)
                            except Exception:
                                continue
                    except Exception:
                        pass
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

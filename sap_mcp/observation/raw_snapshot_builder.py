import json
from typing import Any, Dict, List, Optional
from loguru import logger

class RawSnapshotBuilder:
    """
    Primitive extractor that captures raw SAP GUI control properties.
    """
    
    # Controls that should be treated as "black-box" compound components
    COMPOUND_TYPES = {
        "GuiTableControl",
        "GuiGridView",
        "GuiTree",
        "GuiShell",
        "GuiToolbar",
        "GuiContainerShell"
    }

    def get_raw_snapshot(self, session: Any) -> Dict[str, Any]:
        """
        Captures a raw snapshot of the SAP GUI session.
        Uses GetObjectTree optimization if available (SAP 7.70+).
        """
        try:
            # Attempt optimized capture first (introduced in 7.70)
            if hasattr(session, "GetObjectTree"):
                return self._capture_optimized(session)
        except Exception as e:
            logger.warning(f"Optimized GetObjectTree failed: {e}. Falling back to recursive scan.")

        # Fallback to recursive scan for older SAP versions
        root_data = self._extract_properties(session)
        children = self._collect_recursive(session)
        root_data["children"] = children
        return root_data

    def _capture_optimized(self, session: Any) -> Dict[str, Any]:
        """Uses GetObjectTree to fetch the UI hierarchy in one jump."""
        # We request common properties for all elements
        props = ["Id", "Type", "Text", "Tooltip", "Visible", "Changeable", "Left", "Top", "Width", "Height"]
        
        # GetObjectTree returns a JSON string
        json_str = session.GetObjectTree("", props)
        tree = json.loads(json_str)
        
        # The output of GetObjectTree is slightly different; we translate it 
        # to our internal format or handle it in normalization.
        # For simplicity in this audit, we will post-process the JSON or 
        # let the normalizer handle the schema.
        return {"optimized_tree": tree, "is_optimized": True}

    def _collect_recursive(self, component: Any, depth: int = 0) -> List[Dict[str, Any]]:
        """
        Recursively collects properties of a component and its children.
        Returns a list of dictionaries representing the control hierarchy.
        """
        if not component:
            return []
        
        collected_controls = []
        
        try:
            # Capture current control properties
            props = self._extract_properties(component)
            collected_controls.append(props)
            
            # COMPOUND COMPONENT ISOLATION:
            # If this is a compound type, do NOT recurse into children.
            if props["type"] in self.COMPOUND_TYPES:
                logger.debug(f"Isolating compound component: {props['id']} ({props['type']})")
                return collected_controls

            # Recurse into children if they exist
            if hasattr(component, "Children"):
                children = component.Children
                if children is not None:
                    try:
                        count = children.Count
                        for i in range(count):
                            try:
                                child = children(i)
                                if child:
                                    # Collect children and aggregate their results
                                    collected_controls.extend(self._collect_recursive(child, depth + 1))
                            except Exception:
                                continue
                    except Exception:
                        pass
        except Exception as e:
            logger.debug(f"Error extracting from component {getattr(component, 'Id', 'unknown')}: {str(e)}")

        return collected_controls

    def _extract_properties(self, control: Any) -> Dict[str, Any]:
        """
        Extracts all relevant raw properties from a GuiComponent.
        """
        ctype = str(getattr(control, "Type", ""))
        props = {
            "id": str(getattr(control, "Id", "")),
            "type": ctype,
            "text": str(getattr(control, "Text", "")) if hasattr(control, "Text") else None,
            "tooltip": str(getattr(control, "Tooltip", "")) if hasattr(control, "Tooltip") else None,
            "changeable": bool(getattr(control, "Changeable", False)),
            "visible": bool(getattr(control, "Visible", True)),
            "parent_id": str(getattr(control, "Parent", {}).Id) if getattr(control, "Parent", None) else None,
        }
        
        # Capture position/size
        try:
            if hasattr(control, "Left"):
                props["bounds"] = (int(control.Left), int(control.Top), int(control.Width), int(control.Height))
        except: pass

        # Specialized Metadata for Compound Components
        if ctype == "GuiTableControl":
            props["table_metadata"] = self._extract_table_metadata(control)
        elif ctype == "GuiGridView":
            props["grid_metadata"] = self._extract_grid_metadata(control)
        elif ctype == "GuiTree":
            props["tree_metadata"] = self._extract_tree_metadata(control)
        elif ctype == "GuiShell":
            # For shells, we might want to know the internal subtype
            props["shell_subtype"] = str(getattr(control, "SubType", ""))
            if props["shell_subtype"] == "GridView":
                props["grid_metadata"] = self._extract_grid_metadata(control)

        return props

    def _extract_table_metadata(self, table: Any) -> Dict:
        """Extracts column info and row counts for GuiTableControl."""
        try:
            columns = []
            for i in range(table.Columns.Count):
                col = table.Columns.Item(i)
                columns.append({
                    "name": str(col.Name),
                    "title": str(col.Title),
                    "index": i
                })
            return {
                "columns": columns,
                "row_count": int(table.RowCount),
                "visible_row_count": int(table.VisibleRowCount)
            }
        except: return {}

    def _extract_grid_metadata(self, grid: Any) -> Dict:
        """Extracts column info for GuiGridView (ALV)."""
        try:
            columns = []
            col_names = grid.ColumnOrder
            for name in col_names:
                columns.append({
                    "name": str(name),
                    "title": str(grid.GetColumnToolTip(name)),
                })
            return {
                "columns": columns,
                "row_count": int(grid.RowCount)
            }
        except: return {}

    def _extract_tree_metadata(self, tree: Any) -> Dict:
        """Extracts key structure info for GuiTree."""
        try:
            # Trees can be huge, we only capture a few top nodes as hints
            # Full interaction will happen via search/path tools
            return {
                "hierarchy_strategy": "path_based"
            }
        except: return {}

import time
import datetime
from loguru import logger
from ..engine.sap_engine import SapEngine

def capture_snapshot(session, session_id: str):
    """
    Captures a full snapshot of the current SAP screen.
    Matches the SapScreenSnapshot interface exactly.
    """
    try:
        # 1. Basic Info
        info = SapEngine.get_session_info(session)
        win = session.ActiveWindow
        
        snapshot = {
            "snapshotId": f"snap_{int(time.time())}",
            "sessionId": session_id,
            "capturedAt": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            "sessionInfo": info,
            "window": {
                "title": str(win.Text) if win else "SAP"
            },
            "statusBar": {
                "type": "",
                "text": "",
                "msgId": "",
                "msgNo": "",
                "params": []
            },
            "fields": {},
            "entities": {}
        }
        
        # 2. Status Bar
        try:
            sb = win.StatusBar
            snapshot["statusBar"] = {
                "type": str(sb.MessageType),
                "text": str(sb.Text),
                "msgId": str(getattr(sb, "MessageId", "")),
                "msgNo": str(getattr(sb, "MessageNumber", "")),
                "params": []
            }
        except:
            pass
            
        # 3. Recursive Field Capture
        field_dict = {}
        _collect_fields_recursive(win, field_dict)
        snapshot["fields"] = field_dict
        
        return snapshot
    except Exception as e:
        logger.error(f"Error capturing snapshot: {str(e)}")
        raise

def _collect_fields_recursive(container, field_dict):
    if not container: return
    try:
        children = container.Children
        for i in range(children.Count):
            child = children(i)
            sap_id = str(child.Id)
            
            # Extract rich field info
            field_data = {
                "value": str(child.Text) if hasattr(child, "Text") else None,
                "raw": str(child.Text) if hasattr(child, "Text") else None,
                "editable": bool(getattr(child, "Changeable", False)),
                "visible": bool(getattr(child, "Visible", True)),
                "kind": _map_type_to_kind(str(child.Type)),
                "label": str(getattr(child, "Tooltip", "")) or str(getattr(child, "Text", "")) if "Label" in str(child.Type) else None
            }
            
            field_dict[sap_id] = field_data
            
            # Recurse
            if hasattr(child, "Children"):
                _collect_fields_recursive(child, field_dict)
    except:
        pass

def _map_type_to_kind(sap_type: str) -> str:
    if "GuiLabel" in sap_type: return "label"
    if "GuiTextField" in sap_type or "GuiCTextField" in sap_type: return "text"
    if "GuiCheckBox" in sap_type: return "checkbox"
    if "GuiButton" in sap_type: return "button"
    return "unknown"

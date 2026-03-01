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
        
        logger.debug(f"Capturing snapshot for window: {getattr(win, 'Id', 'unknown')} - {getattr(win, 'Text', 'unknown')}")
        
        snapshot = {
            "id": f"snap_{int(time.time())}",
            "sessionId": session_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            "sessionInfo": info,
            "windowTitle": str(win.Text) if win else "SAP",
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
            sb = getattr(win, "StatusBar", None)
            if not sb:
                # Try fallback access
                try:
                    sb = session.FindById("wnd[0]/sbar")
                except:
                    sb = None
            
            if sb:
                msg_type = str(sb.MessageType) if hasattr(sb, "MessageType") and sb.MessageType else ""
                if msg_type == "None": msg_type = ""
                
                snapshot["statusBar"] = {
                    "type": msg_type,
                    "text": str(sb.Text) if hasattr(sb, "Text") and sb.Text else "",
                    "msgId": str(getattr(sb, "MessageId", "")) if getattr(sb, "MessageId", None) else "",
                    "msgNo": str(getattr(sb, "MessageNumber", "")) if getattr(sb, "MessageNumber", None) else "",
                    "params": []
                }
                if not snapshot["statusBar"]["text"]:
                    try:
                        info = session.Info
                        snapshot["statusBar"]["text"] = str(info.StatusbarText) if info.StatusbarText else ""
                        # Derive type if text exists but type is empty
                        if snapshot["statusBar"]["text"] and not snapshot["statusBar"]["type"]:
                            # Simple heuristic: Error messages usually start with 'E' in background or have an error icon
                            # But Info doesn't give us the type directly easily.
                            pass 
                    except:
                        pass
                
                # Final fallback: search for msgarea if still empty
                if not snapshot["statusBar"]["text"]:
                    try:
                        msg_area = session.FindById("wnd[0]/usr/msgarea")
                        # Usually the first child of msg_area has the text
                        if msg_area.Children.Count > 0:
                            snapshot["statusBar"]["text"] = str(msg_area.Children(0).Text)
                            snapshot["statusBar"]["type"] = "E" # Assume error if in msgarea and we are here
                    except:
                        pass

                logger.debug(f"Status bar captured: {snapshot['statusBar']}")
            else:
                logger.warning("Status bar object not found in current window")
        except Exception as sb_err:
            logger.error(f"Error capturing status bar: {str(sb_err)}")
            
        # 3. Recursive Field Capture
        field_dict = {}
        _collect_fields_recursive(win, field_dict)
        snapshot["fields"] = field_dict
        
        logger.info(f"Captured snapshot with {len(field_dict)} fields")
        logger.info(f"Captured snapshot with ________________ {snapshot} __________________")
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
            raw_id = str(child.Id)
            
            # Normalize ID: /app/con[0]/ses[0]/wnd[0]/... -> wnd[0]/...
            sap_id = raw_id
            if "/wnd[" in raw_id:
                sap_id = "wnd[" + raw_id.split("/wnd[")[-1]
            
            # logger.debug(f"Mapping field: {raw_id} -> {sap_id}")
            
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

from typing import Any, Optional, List, Dict
from loguru import logger
from ..schemas.observation import ScreenObservation
from .busy_guard import BusyGuard
from .modal_guard import ModalGuard
from .com_executor import ComExecutor
from .session_manager import SessionManager

class SapRuntime:
    """
    Coordination layer for SAP GUI scripting.
    Provides a safe, high-level interface for all SAP operations.
    """
    
    def __init__(self):
        self.executor = ComExecutor()
        self.session_manager = SessionManager(self.executor)
        self.busy_guard = BusyGuard()
        self.modal_guard = ModalGuard()

    def get_session(self, session_id: Optional[str] = None) -> Any:
        """
        Retrieves a SAP session object by ID, or the active session if none specified.
        """
        sid = session_id or self.session_manager.active_session_id
        if not sid:
            raise ValueError("No active session and no sessionId provided.")
            
        indices = self.session_manager.get_session_indices(sid)
        if not indices:
            # Try to refresh session list once
            self.session_manager.list_sessions()
            indices = self.session_manager.get_session_indices(sid)
            if not indices:
                raise ValueError(f"Session {sid} not found.")

        conn_idx, sess_idx = indices
        return self.executor.execute(self._do_get_session, conn_idx, sess_idx)

    def _do_get_session(self, conn_idx: int, sess_idx: int) -> Any:
        import win32com.client
        sap_gui_auto = win32com.client.GetObject("SAPGUI")
        application = sap_gui_auto.GetScriptingEngine
        connection = application.Children(conn_idx)
        return connection.Children(sess_idx)


    def list_sessions(self) -> List[Dict]:
        """
        Exposes session discovery.
        """
        return self.session_manager.list_sessions()

    def take_screenshot(self, session: Any) -> Optional[str]:
        """
        Captures a screenshot of the current SAP window and returns it as base64.
        """
        from ..snapshot.screenshot_service import ScreenshotService
        screenshot_service = ScreenshotService()
        
        try:
            hwnd = getattr(session.ActiveWindow, "Handle", 0)
            if hwnd:
                img = screenshot_service.capture_window(int(hwnd))
                if img:
                    return screenshot_service.to_base64(img)
        except Exception as e:
            logger.warning(f"Failed to capture screenshot: {str(e)}")
            
        return None

    def execute_script(self, session: Any, script: str):
        """
        Executes a raw VBScript or internal command if needed.
        Currently a placeholder for advanced escape-hatch interactions.
        """
        logger.info(f"Executing raw script on session {getattr(session, 'Id', 'unknown')}")
        # In a real implementation, this might use session.ExecuteInSession(script)
        # or other low-level primitives depending on requirements.
        pass

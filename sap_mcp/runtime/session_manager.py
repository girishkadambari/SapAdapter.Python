from typing import List, Optional, Dict
from loguru import logger
import win32com.client
from ..schemas.observation import ScreenObservation, StatusBar
from .com_executor import ComExecutor

class SessionManager:
    """
    Discovers and tracks SAP GUI sessions.
    """
    
    def __init__(self, executor: ComExecutor):
        self.executor = executor
        self.active_session_id: Optional[str] = None
        self._sessions: Dict[str, Dict] = {}

    def list_sessions(self) -> List[Dict]:
        """
        Scans all open SAP connections and sessions.
        """
        return self.executor.execute(self._do_list_sessions)

    def _do_list_sessions(self) -> List[Dict]:
        sessions = []
        try:
            sap_gui_auto = win32com.client.GetObject("SAPGUI")
            application = sap_gui_auto.GetScriptingEngine
            
            for i in range(application.Children.Count):
                connection = application.Children(i)
                for j in range(connection.Children.Count):
                    session = connection.Children(j)
                    info = session.Info
                    
                    session_id = f"{i}-{j}"
                    session_data = {
                        "sessionId": session_id,
                        "connection_idx": i,
                        "session_idx": j,
                        "systemId": str(info.SystemName),
                        "client": str(info.Client),
                        "user": str(info.User),
                        "transaction": str(info.Transaction),
                        "title": str(session.ActiveWindow.Text) if session.ActiveWindow else "SAP"
                    }
                    sessions.append(session_data)
                    self._sessions[session_id] = session_data
                    
            return sessions
        except Exception as e:
            logger.error(f"Failed to list SAP sessions: {str(e)}")
            return []

    def get_session_indices(self, session_id: str) -> Optional[tuple]:
        """
        Returns (connection_idx, session_idx) for a given session ID.
        """
        if session_id in self._sessions:
            data = self._sessions[session_id]
            return data["connection_idx"], data["session_idx"]
        return None

    def set_active(self, session_id: str):
        """
        Sets the default active session.
        """
        self.active_session_id = session_id
        logger.info(f"Active SAP session set to: {session_id}")

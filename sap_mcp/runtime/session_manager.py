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
            
            children = application.Children
            if children is None:
                return []
                
            for i in range(children.Count):
                connection = children(i)
                
                # Active sessions are children of a connection
                # Using .Sessions is more explicit for SAP GUI
                try:
                    sessions_coll = connection.Sessions
                    if sessions_coll is None:
                        continue
                        
                    for j in range(sessions_coll.Count):
                        session = sessions_coll(j)
                        info = session.Info
                        session_id = f"{i}-{j}"
                        
                        # Get window title safely
                        title = "SAP"
                        try:
                            if session.ActiveWindow:
                                title = str(session.ActiveWindow.Text)
                        except Exception:
                            pass

                        session_data = {
                            "sessionId": session_id,
                            "connection_idx": i,
                            "session_idx": j,
                            "systemId": str(info.SystemName),
                            "client": str(info.Client),
                            "user": str(info.User),
                            "transaction": str(info.Transaction),
                            "title": title
                        }
                        sessions.append(session_data)
                        self._sessions[session_id] = session_data
                except Exception as e:
                    logger.warning(f"Failed to enumerate sessions for connection {i}: {str(e)}")
                    
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

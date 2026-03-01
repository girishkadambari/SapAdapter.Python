# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/engine/sap_engine.py
import win32com.client
import pythoncom
from loguru import logger
from typing import Any, Optional

class SapEngine:
    """
    Handles COM interaction with SAP GUI Scripting Engine.
    Matches the logic of the user's working VBScript.
    """
    
    @staticmethod
    def get_scripting_engine() -> Any:
        """
        Acquires the SAP GUI Scripting Engine using win32com.
        """
        try:
            # Initialize COM for this thread (Crucial for multithreading)
            pythoncom.CoInitialize()
            
            logger.debug("Attempting to get SAPGUI object via GetObject...")
            # This is exactly what the user's VBScript does: Set SapGuiAuto = GetObject("SAPGUI")
            sap_gui_auto = win32com.client.GetObject("SAPGUI")
            if not sap_gui_auto:
                logger.error("SAPGUI object not found in ROT.")
                return None
                
            logger.debug("Acquiring scripting engine from SapGuiAuto...")
            application = sap_gui_auto.GetScriptingEngine
            if not application:
                logger.error("Failed to get Scripting Engine from SAPGUI object.")
                return None
                
            return application
        except Exception as e:
            logger.error(f"COM Error during engine discovery: {str(e)}")
            raise
            
    @staticmethod
    def list_sessions(engine: Any) -> list:
        """
        Lists all active SAP sessions.
        """
        sessions = []
        try:
            for i in range(engine.Children.Count):
                connection = engine.Children(i)
                for j in range(connection.Children.Count):
                    session = connection.Children(j)
                    info = session.Info
                    
                    sessions.append({
                        "sessionId": f"{i}-{j}",
                        "systemId": str(info.SystemName),
                        "client": str(info.Client),
                        "user": str(info.User),
                        "transaction": str(info.Transaction),
                        "program": str(info.Program),
                        "screenNumber": str(info.ScreenNumber),
                        "windowTitle": str(session.ActiveWindow.Text) if session.ActiveWindow else "SAP"
                    })
            return sessions
        except Exception as e:
            logger.warning(f"Error listing sessions: {str(e)}")
            return []

    @staticmethod
    def get_session_info(session: Any) -> dict:
        """
        Extracts technical session info.
        """
        try:
            info = session.Info
            return {
                "systemId": str(info.SystemName),
                "client": str(info.Client),
                "user": str(info.User),
                "language": str(info.Language),
                "server": str(info.MessageServer),
                "scriptingModeReadOnly": bool(info.IsReadOnly),
                "transaction": str(info.Transaction),
                "program": str(info.Program),
                "dynpro": str(info.ScreenNumber), # Mapping ScreenNumber to dynpro
                "screenNumber": str(info.ScreenNumber)
            }
        except Exception as e:
            logger.error(f"Error getting session info: {str(e)}")
            return {}

    @staticmethod
    def get_session(engine: Any, connection_idx: int, session_idx: int) -> Optional[Any]:
        """
        Helper to get a specific session object.
        """
        try:
            connection = engine.Children(connection_idx)
            session = connection.Children(session_idx)
            return session
        except Exception as e:
            logger.error(f"Session {connection_idx}-{session_idx} not found: {str(e)}")
            return None

# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/engine/session_manager.py
from typing import Dict, Optional, Any
from loguru import logger

class SessionManager:
    """
    Manages registered SAP sessions for the adapter.
    """
    def __init__(self):
        # Maps sessionId (e.g. "0-0") to (connection_index, session_index)
        self.registry: Dict[str, tuple] = {}
        self.active_session_id: Optional[str] = None

    def register(self, session_id: str, conn_idx: int, ses_idx: int):
        self.registry[session_id] = (conn_idx, ses_idx)
        logger.info(f"Registered session {session_id} -> ({conn_idx}, {ses_idx})")

    def get_indices(self, session_id: str) -> Optional[tuple]:
        return self.registry.get(session_id)

    def set_active(self, session_id: str):
        if session_id in self.registry:
            self.active_session_id = session_id
            logger.info(f"Active session set to: {session_id}")
        else:
            logger.warning(f"Cannot set active session: {session_id} not in registry.")

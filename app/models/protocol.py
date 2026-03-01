# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/models/protocol.py
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List

class ErrorModel(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None

class RequestModel(BaseModel):
    id: str  # Correlation ID
    type: str  # One of: healthCheck, listSessions, attachSession, captureSnapshot, executeCommand
    payload: Optional[Dict[str, Any]] = None

class ResponseModel(BaseModel):
    id: str  # Matches request ID
    ok: bool = True
    payload: Optional[Any] = None
    error: Optional[ErrorModel] = None

class EventModel(BaseModel):
    type: str = "event"
    event: str  # e.g., snapshot.created
    payload: Dict[str, Any]

class SessionListItem(BaseModel):
    sessionId: str
    systemId: str
    client: str
    user: str
    transaction: str
    windowTitle: str

class SapCommand(BaseModel):
    id: str
    title: str
    type: str # navigateTcode, etc.
    risk: str # SAFE, CONFIRM, BLOCKED
    permissionRequired: str
    payload: Dict[str, Any]
    preview: Optional[str] = None

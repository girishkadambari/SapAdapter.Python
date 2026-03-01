# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/main.py
import asyncio
import os
from app.logger import setup_logger
from app.server import WebSocketServer
from app.commands.router import CommandRouter
from app.engine.sap_engine import SapEngine
from app.engine.session_manager import SessionManager

# Setup Logger
logger = setup_logger()

from app.commands.handlers.execute import execute_command
from app.snapshot.pipeline import capture_snapshot

# Shared instances
session_manager = SessionManager()
server = None

def get_session_from_payload(payload):
    # Electron app sends sessionId in payload for executeCommand and captureSnapshot
    session_id = payload.get("sessionId") or session_manager.active_session_id
    if not session_id:
        raise Exception("No active session. Please attach to or list sessions first.")
    
    indices = session_manager.get_indices(session_id)
    if not indices:
        raise Exception(f"Session {session_id} not found in adapter registry")
        
    engine = SapEngine.get_scripting_engine()
    return SapEngine.get_session(engine, indices[0], indices[1])

import pythoncom

async def monitor_screen():
    """
    Background task to monitor for screen changes in the active session.
    """
    pythoncom.CoInitialize()
    last_tx = None
    last_title = None
    
    while True:
        try:
            if session_manager.active_session_id and server:
                # We need to get a fresh engine reference for this thread if needed,
                # but get_session_from_payload handles that.
                session = get_session_from_payload({})
                info = session.Info
                current_tx = str(info.Transaction)
                current_title = str(session.ActiveWindow.Text) if session.ActiveWindow else ""
                
                if current_tx != last_tx or current_title != last_title:
                    logger.info(f"Screen changed: {current_tx} - {current_title}")
                    await server.broadcast("screen.changed", {
                        "sessionId": session_manager.active_session_id,
                        "transaction": current_tx,
                        "title": current_title
                    })
                    last_tx = current_tx
                    last_title = current_title
        except Exception as e:
            # Silent skip if COM is busy or no active session
            pass
            
        await asyncio.sleep(2) # Poll every 2 seconds

async def list_sessions_handler(ctx, payload):
    logger.info("Listing SAP sessions...")
    engine = SapEngine.get_scripting_engine()
    if not engine:
        raise Exception("SAP Scripting Engine not available")
    
    sessions = SapEngine.list_sessions(engine)
    
    # Auto-register found sessions
    for s in sessions:
        parts = s["sessionId"].split("-")
        session_manager.register(s["sessionId"], int(parts[0]), int(parts[1]))
    
    # Auto-set active if none
    if sessions and not session_manager.active_session_id:
        session_manager.set_active(sessions[0]["sessionId"])
        
    return sessions

async def attach_session_handler(ctx, payload):
    session_id = payload.get("sessionId")
    if not session_id:
        raise ValueError("sessionId required for attachSession")
        
    session_manager.set_active(session_id)
    return {"status": "attached", "sessionId": session_id}

async def capture_snapshot_handler(ctx, payload):
    session_id = payload.get("sessionId") or session_manager.active_session_id
    session = get_session_from_payload(payload)
    return capture_snapshot(session, session_id)

async def execute_command_handler(ctx, payload):
    # payload is a SapCommand object
    session = get_session_from_payload(payload)
    return await execute_command(session, payload)

async def health_check_handler(ctx, payload):
    return {"status": "ok", "provider": "python-com"}

async def main():
    global server
    logger.info("Initializing SAP Copilot Adapter (Python Edition)")
    
    # Initialize Core Components
    router = CommandRouter()
    
    # Register Protocol Handlers (Matching AdapterRequestType)
    router.register("healthCheck", health_check_handler)
    router.register("listSessions", list_sessions_handler)
    router.register("attachSession", attach_session_handler)
    router.register("captureSnapshot", capture_snapshot_handler)
    router.register("executeCommand", execute_command_handler)
    
    # Start Server
    port = int(os.getenv("PORT", 8787))
    server = WebSocketServer("0.0.0.0", port, router)
    
    # Start Screen Monitor in background
    asyncio.create_task(monitor_screen())
    
    await server.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")

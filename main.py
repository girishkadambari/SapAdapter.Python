import asyncio
import os
import json
import pythoncom
from sap_mcp.utils.logger import setup_logger
from sap_mcp.server.websocket import WebSocketServer
from sap_mcp.server.router import CommandRouter
from sap_mcp.runtime.sap_runtime import SapRuntime
from sap_mcp.mcp.mcp_adapter import McpAdapter
from sap_mcp.mcp.mcp_server import McpServer
from sap_mcp.observation.screen_observation_builder import ScreenObservationBuilder
from sap_mcp.execution.action_dispatcher import ActionDispatcher
from sap_mcp.schemas.action import ActionRequest

# Setup Logger
logger = setup_logger()

# Global Instances for Legacy Support
runtime = SapRuntime()
observation_builder = ScreenObservationBuilder(runtime)
action_dispatcher = ActionDispatcher(runtime)
server = None

async def list_sessions_handler(ctx, payload):
    logger.info("Listing SAP sessions via new runtime...")
    return runtime.list_sessions()

async def attach_session_handler(ctx, payload):
    session_id = payload.get("sessionId")
    if not session_id:
        raise ValueError("sessionId required for attachSession")
    runtime.session_manager.set_active(session_id)
    return {"status": "attached", "sessionId": session_id}

async def capture_snapshot_handler(ctx, payload):
    session_id = payload.get("sessionId")
    include_ss = payload.get("includeScreenshot", False)
    observation = await observation_builder.build(session_id, include_screenshot=include_ss)
    return observation.model_dump()

async def execute_command_handler(ctx, payload):
    # Map legacy payload to new ActionRequest
    session_id = payload.get("sessionId") or runtime.session_manager.active_session_id
    action_type = payload.get("type", "press")
    target_id = payload.get("id") or payload.get("target_id")
    
    if not target_id:
        raise ValueError("target_id (or 'id') is required for executeCommand")
        
    request = ActionRequest(
        session_id=str(session_id),
        target_id=str(target_id),
        action_type=str(action_type),
        params=payload.get("payload", {})
    )
    result = await action_dispatcher.execute(request)
    return result.model_dump()

async def health_check_handler(ctx, payload):
    return {"status": "ok", "provider": "sap_mcp"}

async def monitor_screen():
    """
    Background task to monitor for screen changes in the active session.
    """
    pythoncom.CoInitialize()
    last_tx = None
    last_title = None
    
    while True:
        try:
            sid = runtime.session_manager.active_session_id
            if sid and server:
                session = runtime.get_session(sid)
                info = session.Info
                current_tx = str(info.Transaction)
                current_title = str(session.ActiveWindow.Text) if session.ActiveWindow else ""
                
                if current_tx != last_tx or current_title != last_title:
                    logger.info(f"Screen changed: {current_tx} - {current_title}")
                    await server.broadcast("screen.changed", {
                        "sessionId": sid,
                        "transaction": current_tx,
                        "title": current_title
                    })
                    last_tx = current_tx
                    last_title = current_title
        except Exception:
            pass
            
        await asyncio.sleep(2)

async def main():
    global server
    logger.info("Initializing SAP MCP Server")
    
    # Initialize Core Components
    router = CommandRouter()
    
    # Initialize MCP Adapter and Server
    mcp_adapter = McpAdapter(runtime)
    mcp_server = McpServer(mcp_adapter)
    
    # Register Legacy Protocol Handlers
    router.register("healthCheck", health_check_handler)
    router.register("listSessions", list_sessions_handler)
    router.register("attachSession", attach_session_handler)
    router.register("captureSnapshot", capture_snapshot_handler)
    router.register("executeCommand", execute_command_handler)
    
    # Start Server
    port = int(os.getenv("PORT", 8787))
    server = WebSocketServer("0.0.0.0", port, router)
    server.mcp_server = mcp_server
    
    # Start Screen Monitor
    asyncio.create_task(monitor_screen())
    
    await server.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped.")

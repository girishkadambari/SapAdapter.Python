# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/engine/wait_helper.py
import asyncio
from loguru import logger

async def wait_for_idle(session: Any, timeout_ms: int = 20000):
    """
    Waits for a SAP session to become idle by polling session.Busy.
    """
    start_time = asyncio.get_event_loop().time()
    timeout_sec = timeout_ms / 1000.0
    poll_interval = 0.5

    logger.debug(f"Waiting for session idle (timeout: {timeout_ms}ms)...")

    while (asyncio.get_event_loop().time() - start_time) < timeout_sec:
        try:
            if not session.Busy:
                # Additional check for status bar
                try:
                    status_bar = session.ActiveWindow.StatusBar
                    text = status_bar.Text if status_bar else ""
                    if "Please wait" not in text and "System busy" not in text:
                        return
                except:
                    # Status bar not available, consider idle
                    return
        except Exception as e:
            logger.warning(f"Error checking session busy state: {str(e)}")
            
        await asyncio.sleep(poll_interval)

    logger.warning(f"Wait for idle timed out after {timeout_ms}ms")

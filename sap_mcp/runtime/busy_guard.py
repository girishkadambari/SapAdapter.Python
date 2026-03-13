import asyncio
import time
from typing import Any
from loguru import logger

class BusyGuard:
    """
    Ensures SAP is ready for interaction by waiting for session.Busy and status bar indicators.
    """
    
    def __init__(self, timeout_ms: int = 30000, poll_interval_ms: int = 500):
        self.timeout_sec = timeout_ms / 1000.0
        self.poll_interval_sec = poll_interval_ms / 1000.0

    async def wait_for_idle(self, session: Any):
        """
        Polls until the session is not busy.
        """
        start_time = time.time()
        
        while (time.time() - start_time) < self.timeout_sec:
            try:
                if not session.Busy:
                    # Double check status bar for "Please wait" or "System busy"
                    try:
                        sb = session.ActiveWindow.StatusBar
                        text = sb.Text.lower() if sb and sb.Text else ""
                        if "please wait" not in text and "system busy" not in text:
                            return
                    except:
                        # If status bar access fails, assume idle if Busy is false
                        return
            except Exception as e:
                logger.debug(f"Error checking busy state (transient): {str(e)}")
            
            await asyncio.sleep(self.poll_interval_sec)
            
        logger.warning(f"Wait for idle timed out after {self.timeout_sec}s")
        raise TimeoutError(f"SAP session remains busy after {self.timeout_sec}s")

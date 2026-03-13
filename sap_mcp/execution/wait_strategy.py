import asyncio
import time
from typing import Any, Callable, Optional
from loguru import logger
from ..runtime.sap_runtime import SapRuntime
from ..runtime.busy_guard import BusyGuard

class WaitStrategy:
    """
    Provides deterministic wait logic for SAP GUI state transitions.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime

    async def wait_for_idle(self, session: Any, timeout: float = 30.0):
        """
        Waits until the SAP session is no longer busy.
        """
        await self.runtime.busy_guard.wait_for_idle(session, timeout=timeout)

    async def wait_for_condition(self, condition_fn: Callable[[], bool], timeout: float = 10.0, poll_interval: float = 0.5) -> bool:
        """
        Polls until a condition is met or timeout occurs.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_fn():
                return True
            await asyncio.sleep(poll_interval)
        return False

    async def wait_for_status_change(self, session: Any, initial_text: str, timeout: float = 10.0) -> bool:
        """
        Waits until the status bar text changes from its initial value.
        """
        def status_changed():
            try:
                return str(session.ActiveWindow.StatusBar.Text) != initial_text
            except:
                return False
                
        return await self.wait_for_condition(status_changed, timeout=timeout)

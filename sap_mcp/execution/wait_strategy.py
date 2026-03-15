import asyncio
from typing import Any, Optional
from loguru import logger
from ..runtime.sap_runtime import SapRuntime

class WaitStrategy:
    """
    Standardizes "wait for result" and "ensure ready" logic.
    Provides consistent behavior across all action handlers.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime

    async def wait_for_ready(self, session: Any, timeout: int = 30):
        """
        Waits for SAP to be idle and ensures no blocking modals.
        """
        start_time = asyncio.get_event_loop().time()
        
        # 1. Busy Guard
        await self.runtime.busy_guard.wait_for_idle(session, timeout=timeout)
        
        # 2. Modal Guard
        modal = self.runtime.modal_guard.detect(session)
        if modal:
            logger.warning(f"Blocking modal detected during wait: {modal.title}")
            return modal
        
        return None

    async def wait_after_action(self, session: Any, timeout: int = 5):
        """
        Brief wait after an action to let the GUI settle.
        """
        await asyncio.sleep(0.5)  # Micro-wait
        await self.runtime.busy_guard.wait_for_idle(session, timeout=timeout)

from abc import ABC, abstractmethod
from typing import Any, Dict
from loguru import logger
from ...schemas import ActionRequest, ActionResult
from ...runtime.sap_runtime import SapRuntime
from ..wait_strategy import WaitStrategy
from ...observation.screen_observation_builder import ScreenObservationBuilder

class ActionHandler(ABC):
    """
    Abstract base class for all SAP action handlers.
    """
    def __init__(self, runtime: SapRuntime, wait_strategy: WaitStrategy, observation_builder: ScreenObservationBuilder):
        self.runtime = runtime
        self.wait_strategy = wait_strategy
        self.observation_builder = observation_builder

    @abstractmethod
    async def execute(self, session: Any, request: ActionRequest) -> ActionResult:
        """
        Execute the specific action on the given session.
        """
        pass

    def _normalize_target_id(self, target_id: str) -> str:
        """Remove leading slashes which can cause FindById failure."""
        if not target_id:
            return ""
        if target_id.startswith("/"):
            return target_id.lstrip("/")
        return target_id

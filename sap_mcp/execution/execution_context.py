from typing import Any, List, Optional
from datetime import datetime
from ..schemas.observation import ScreenObservation
from ..schemas.action import ActionRequest

class ExecutionContext:
    """
    Manages the state and history of an ongoing execution sequence.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[ActionRequest] = []
        self.observations: List[ScreenObservation] = []
        self.start_time = datetime.now()

    def record_action(self, request: ActionRequest):
        self.history.append(request)

    def record_observation(self, observation: ScreenObservation):
        self.observations.append(observation)

    @property
    def last_observation(self) -> Optional[ScreenObservation]:
        return self.observations[-1] if self.observations else None

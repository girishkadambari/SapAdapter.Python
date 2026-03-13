from pydantic import BaseModel, Field

class TimeoutPolicy(BaseModel):
    """
    Defines configurable timeouts for different SAP operations.
    """
    idle_wait_ms: int = Field(30000, description="Timeout for waiting for SAP to be idle")
    action_settle_ms: int = Field(2000, description="Time to wait after an action for the UI to settle")
    observation_ms: int = Field(10000, description="Timeout for capturing a screen observation")
    connection_ms: int = Field(5000, description="Timeout for attaching to a session")

DEFAULT_TIMEOUT_POLICY = TimeoutPolicy()

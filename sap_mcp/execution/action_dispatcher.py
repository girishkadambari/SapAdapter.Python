from typing import Any, Dict, Optional
"""
Action execution pipeline.
Deterministic routing and execution of UI interactions with post-action verification.
"""
from loguru import logger
from ..schemas import ActionRequest, ActionResult
from ..runtime.sap_runtime import SapRuntime
from .wait_strategy import WaitStrategy
from ..observation.screen_observation_builder import ScreenObservationBuilder

class ActionDispatcher:
    """
    Central engine for executing SAP GUI actions reliably.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime
        self.wait_strategy = WaitStrategy(runtime)
        self.observation_builder = ScreenObservationBuilder(runtime)

    async def execute(self, request: ActionRequest) -> ActionResult:
        """
        Executes a standardized ActionRequest.
        """
        logger.info(f"Executing action: {request.action_type} on {request.target_id}")
        
        session = self.runtime.get_session(request.session_id)
        
        # 1. Ensure SAP is ready
        await self.runtime.ensure_ready(session)
        
        initial_status = ""
        try:
             initial_status = str(session.ActiveWindow.StatusBar.Text)
        except:
             pass

        # 2. Find target and execute
        try:
            target = session.FindById(request.target_id)
            
            # Execute based on action type
            if request.action_type == "set_text":
                target.Text = request.params.get("value")
            elif request.action_type == "press":
                target.Press()
            elif request.action_type == "select":
                # Handles tabs, radio buttons, or menu items
                if hasattr(target, "Select"):
                    target.Select()
                elif hasattr(target, "Selected"):
                    target.Selected = True
            elif request.action_type == "set_value":
                # For checkboxes or other value-based toggles
                if hasattr(target, "Key"):
                    target.Key = request.params.get("value")
                else:
                    target.Text = request.params.get("value")
            else:
                raise ValueError(f"Unsupported action type: {request.action_type}")
                
            # 3. Wait for post-action stability
            await self.wait_strategy.wait_for_idle(session)
            
            # 4. Capture result
            observation = await self.observation_builder.build(request.session_id)
            
            return ActionResult(
                success=True,
                observation=observation,
                message=f"Action {request.action_type} executed successfully."
            )

        except Exception as e:
            logger.error(f"Action execution failed: {str(e)}")
            # Even on failure, try to capture state for debugging
            try:
                observation = await self.observation_builder.build(request.session_id)
            except:
                observation = None
                
            return ActionResult(
                success=False,
                error=str(e),
                observation=observation
            )

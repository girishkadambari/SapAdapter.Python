from typing import Any, Dict, Optional
"""
Action execution pipeline.
Deterministic routing and execution of UI interactions with post-action verification.
"""
from loguru import logger
from ..core.config import Config, ActionTypes, StatusBarTypes
from ..schemas import ActionRequest, ActionResult
from ..runtime.sap_runtime import SapRuntime
from .wait_strategy import WaitStrategy
from ..observation.screen_observation_builder import ScreenObservationBuilder

from .action_registry import ActionRegistry

class ActionDispatcher:
    """
    Central engine for routing SAP GUI actions reliably via defined handlers.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime
        self.wait_strategy = WaitStrategy(runtime)
        self.observation_builder = ScreenObservationBuilder(runtime)
        self.registry = ActionRegistry()

    async def execute(self, request: ActionRequest) -> ActionResult:
        """
        Routes the ActionRequest to the correct handler and captures rich results.
        """
        logger.info(f"Executing action: {request.action_type} on {request.target_id}")
        session = self.runtime.get_session(request.session_id)
        
        # 1. Ensure SAP is ready (Pre-action)
        await self.wait_strategy.wait_for_ready(session)
        
        # 2. Get Handler
        try:
            handler_cls = self.registry.get_handler_class(request.action_type)
        except ValueError as e:
            return ActionResult(
                success=False,
                action_type=request.action_type,
                target_id=request.target_id,
                error=str(e)
            )
            
        handler = handler_cls(self.runtime, self.wait_strategy, self.observation_builder)
        
        # 3. Execute via handler
        try:
            result = await handler.execute(session, request)
        except Exception as e:
            result = ActionResult(
                success=False,
                action_type=request.action_type,
                target_id=request.target_id,
                error=str(e)
            )

        # 4. Post-action verification and observation
        await self.wait_strategy.wait_after_action(session)
        
        try:
            # Mode="SUMMARY" provides agentic context for the next step
            observation = await self.observation_builder.build(request.session_id, mode="SUMMARY")
            result.observation = observation
            
            # Enrich AI-specific fields from Status Bar
            if observation and observation.status_bar:
                if observation.status_bar.type in (StatusBarTypes.WARNING, StatusBarTypes.ERROR, StatusBarTypes.ABORT):
                    result.warnings.append(f"[{observation.status_bar.type}] {observation.status_bar.text}")
                    if observation.status_bar.type in (StatusBarTypes.ERROR, StatusBarTypes.ABORT):
                        result.success = False
                        result.error = observation.status_bar.text
                
                result.is_modal_active = bool(observation.modal)
                
            result.verification_outcome = "SUCCESS" if result.success else "FAILED"
        except Exception as e:
            logger.error(f"Failed to capture post-action observation: {str(e)}")
            result.verification_outcome = "UNVERIFIED"
            
        return result

    async def execute_batch(self, session_id: str, requests: list[ActionRequest]) -> list[ActionResult]:
        """
        Executes a sequence of actions. Stops on the first critical error.
        """
        results = []
        for i, req in enumerate(requests):
            logger.info(f"Batch execution step {i+1}/{len(requests)}: {req.action_type}")
            result = await self.execute(req)
            results.append(result)
            
            if not result.success:
                logger.warning(f"Batch execution halted at step {i+1} due to failure: {result.error}")
                # Add step info to result for better agent debugging
                result.message = f"Batch failed at step {i+1}: {result.message or ''}"
                break
                
        return results

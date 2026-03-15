from typing import Any, Dict, Optional
from .base_tool import BaseMcpTool
from ...observation.screen_observation_builder import ScreenObservationBuilder

class SapGetScreenSummaryTool(BaseMcpTool):
    def __init__(self, observation_builder: ScreenObservationBuilder):
        self.observation_builder = observation_builder

    @property
    def name(self) -> str:
        return "sap_get_screen_summary"

    @property
    def description(self) -> str:
        return (
            "PURPOSE: Fast high-level understanding of the current screen.\n"
            "WHEN TO USE: Always use this as the default observation tool. "
            "It returns window metadata, status bar info, and only 'high-value' controls."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string", "description": "The SAP session identifier." }
            },
            "required": ["session_id"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            sid = arguments.get("session_id")
            observation = await self.observation_builder.build(sid, mode="SUMMARY")
            return self._success_response(observation.model_dump_json())
        except Exception as e:
            return self._error_response(str(e))

class SapInspectControlTool(BaseMcpTool):
    def __init__(self, observation_builder: ScreenObservationBuilder):
        self.observation_builder = observation_builder

    @property
    def name(self) -> str:
        return "sap_inspect_control"

    @property
    def description(self) -> str:
        return (
            "PURPOSE: Detailed property extraction for a specific control.\n"
            "WHEN TO USE: Call this when you have a target_id from the summary and need full details."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string" },
                "target_id": { "type": "string", "description": "The absolute SAP ID of the control." }
            },
            "required": ["session_id", "target_id"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            sid = arguments.get("session_id")
            tid = arguments.get("target_id")
            observation = await self.observation_builder.build(sid, mode="FOCUSED", target_id=tid)
            return self._success_response(observation.model_dump_json())
        except Exception as e:
            return self._error_response(str(e))

class SapCaptureVisualTool(BaseMcpTool):
    def __init__(self, observation_builder: ScreenObservationBuilder):
        self.observation_builder = observation_builder

    @property
    def name(self) -> str:
        return "sap_capture_visual"

    @property
    def description(self) -> str:
        return (
            "PURPOSE: Visual verification without payload bloat.\n"
            "WHEN TO USE: Use for debugging or verifying complex layouts."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string" },
                "save_path": { "type": "string", "description": "Optional absolute path to save the image." }
            },
            "required": ["session_id"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from ...core.config import Config
            sid = arguments.get("session_id")
            save_path = arguments.get("save_path") or Config.get_screenshot_path(f"sap_{sid}.png")
            
            observation = await self.observation_builder.build(sid, include_screenshot=True)
            
            if observation.screenshot_data:
                import base64
                with open(save_path, "wb") as f:
                    f.write(base64.b64decode(observation.screenshot_data))
                return self._success_response(f"Screenshot saved to: {save_path}")
            return self._error_response("Failed to capture screenshot.")
        except Exception as e:
            return self._error_response(str(e))

class SapObserveScreenTool(BaseMcpTool):
    def __init__(self, observation_builder: ScreenObservationBuilder):
        self.observation_builder = observation_builder

    @property
    def name(self) -> str:
        return "sap_observe_screen"

    @property
    def description(self) -> str:
        return "DEPRECATED: Use 'get_screen_summary' instead. PURPOSE: Full UI state dump."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": { "type": "string" },
                "include_screenshot": { "type": "boolean", "default": False }
            },
            "required": ["session_id"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            sid = arguments.get("session_id")
            include_ss = arguments.get("include_screenshot", False)
            observation = await self.observation_builder.build(sid, include_screenshot=include_ss, mode="FULL")
            return self._success_response(observation.model_dump_json())
        except Exception as e:
            return self._error_response(str(e))

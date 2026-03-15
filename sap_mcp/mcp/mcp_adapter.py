from typing import Any, Dict, List, Optional
from loguru import logger

from ..runtime.sap_runtime import SapRuntime
from ..observation.screen_observation_builder import ScreenObservationBuilder
from ..execution.action_dispatcher import ActionDispatcher
from ..extraction.entity_extractor import EntityExtractor
from ..schemas import ActionRequest

from .tool_definitions import get_tool_definitions

class McpAdapter:
    """
    Adapter that bridges MCP protocol calls to internal SAP services.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime
        self.observation_builder = ScreenObservationBuilder(runtime)
        self.action_dispatcher = ActionDispatcher(runtime)
        self.entity_extractor = EntityExtractor()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Returns the list of available MCP tools.
        """
        return get_tool_definitions()

    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches an MCP tool call to the appropriate internal service.
        """
        try:
            if name == "list_sessions":
                sessions = self.runtime.list_sessions()
                return {"content": [{"type": "text", "text": str(sessions)}]}

            elif name == "get_screen_summary":
                sid = arguments.get("session_id")
                observation = await self.observation_builder.build(sid, mode="SUMMARY")
                return {"content": [{"type": "text", "text": observation.model_dump_json()}]}

            elif name == "inspect_control":
                sid = arguments.get("session_id")
                tid = arguments.get("target_id")
                observation = await self.observation_builder.build(sid, mode="FOCUSED", target_id=tid)
                return {"content": [{"type": "text", "text": observation.model_dump_json()}]}

            elif name == "capture_visual":
                sid = arguments.get("session_id")
                save_path = arguments.get("save_path")
                if not save_path:
                    import os, tempfile
                    from datetime import datetime
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = os.path.join(tempfile.gettempdir(), f"sap_screenshot_{ts}.png")
                
                observation = await self.observation_builder.build(sid, include_screenshot=True)
                
                if observation.screenshot_data:
                    import base64
                    with open(save_path, "wb") as f:
                        f.write(base64.b64decode(observation.screenshot_data))
                    
                    return {
                        "content": [
                            {
                                "type": "text", 
                                "text": f"Screenshot saved to: {save_path}\nWindow: {observation.title} ({observation.transaction})"
                            }
                        ]
                    }
                else:
                    return {"isError": True, "content": [{"type": "text", "text": "Failed to capture screenshot."}]}

            elif name == "observe_screen":
                sid = arguments.get("session_id")
                include_ss = arguments.get("include_screenshot", False)
                force_rec = arguments.get("force_recursive", False) # Legacy support
                observation = await self.observation_builder.build(
                    sid, 
                    include_screenshot=include_ss, 
                    force_recursive=force_rec,
                    mode="FULL"
                )
                return {"content": [{"type": "text", "text": observation.model_dump_json()}]}

            elif name == "sap_navigate":
                request = ActionRequest(
                    session_id=arguments["session_id"],
                    action_type=arguments["action_type"],
                    params={"tcode": arguments.get("tcode"), "vkey": arguments.get("vkey", 0)}
                )
                result = await self.action_dispatcher.execute(request)
                return {"content": [{"type": "text", "text": result.model_dump_json()}]}
                
            elif name == "sap_interact_field":
                request = ActionRequest(
                    session_id=arguments["session_id"],
                    target_id=arguments["target_id"],
                    action_type=arguments["action_type"],
                    params={"value": arguments.get("value")}
                )
                result = await self.action_dispatcher.execute(request)
                return {"content": [{"type": "text", "text": result.model_dump_json()}]}
                
            elif name == "sap_press_button":
                request = ActionRequest(
                    session_id=arguments["session_id"],
                    target_id=arguments["target_id"],
                    action_type="press_button",
                )
                result = await self.action_dispatcher.execute(request)
                return {"content": [{"type": "text", "text": result.model_dump_json()}]}
                
            elif name == "sap_table_action":
                request = ActionRequest(
                    session_id=arguments["session_id"],
                    target_id=arguments["target_id"],
                    action_type=arguments["action_type"],
                    params={
                        "row": arguments.get("row"),
                        "column": arguments.get("column"),
                        "value": arguments.get("value"),
                        "rows": arguments.get("rows")
                    }
                )
                result = await self.action_dispatcher.execute(request)
                return {"content": [{"type": "text", "text": result.model_dump_json()}]}

            elif name == "sap_tree_action":
                request = ActionRequest(
                    session_id=arguments["session_id"],
                    target_id=arguments["target_id"],
                    action_type=arguments["action_type"],
                    params={"node_key": arguments.get("node_key")}
                )
                result = await self.action_dispatcher.execute(request)
                return {"content": [{"type": "text", "text": result.model_dump_json()}]}

            elif name == "sap_shell_action":
                request = ActionRequest(
                    session_id=arguments["session_id"],
                    target_id=arguments["target_id"],
                    action_type=arguments["action_type"],
                    params={"button_id": arguments.get("button_id")}
                )
                result = await self.action_dispatcher.execute(request)
                return {"content": [{"type": "text", "text": result.model_dump_json()}]}

            elif name == "execute_batch":
                sid = arguments["session_id"]
                action_dicts = arguments["actions"]
                
                requests = []
                for ad in action_dicts:
                    # Specialized mapping of tool-specific arguments to internal params
                    tool_params = ad.get("params", {})
                    
                    # If this came from a tool-specific call via MCP, 
                    # we need to ensure known keys are mapped if missing in params.
                    # This handles the case where the agent might flat-map parameters.
                    if ad.get("tool") == "sap_table_action":
                        for k in ["row", "column", "value"]:
                            if k in ad and k not in tool_params:
                                tool_params[k] = ad[k]
                    elif ad.get("tool") == "sap_interact_field":
                        if "value" in ad and "value" not in tool_params:
                            tool_params["value"] = ad["value"]
                    elif ad.get("tool") == "sap_navigate":
                        for k in ["tcode", "vkey"]:
                            if k in ad and k not in tool_params:
                                tool_params[k] = ad[k]

                    requests.append(ActionRequest(
                        session_id=sid,
                        target_id=ad.get("target_id"),
                        action_type=ad["action_type"],
                        params=tool_params
                    ))
                
                results = await self.action_dispatcher.execute_batch(sid, requests)
                return {"content": [{"type": "text", "text": f"Executed {len(results)}/{len(requests)} actions.\n" + "\n".join([r.model_dump_json() for r in results])}]}

            elif name == "extract_entity":
                sid = arguments["session_id"]
                entity_type = arguments["entity_type"]
                observation = await self.observation_builder.build(sid)
                extraction = self.entity_extractor.extract_entity(observation, entity_type)
                return extraction.model_dump_json() if hasattr(extraction, 'model_dump_json') else str(extraction)
            
            elif name == "get_sap_context":
                sid = arguments.get("session_id")
                context = await self.observation_builder.build_context(sid)
                return {"content": [{"type": "text", "text": str(context)}]}

            elif name == "get_status_and_incompletion":
                sid = arguments.get("session_id")
                verification = await self.observation_builder.build_verification(sid)
                return {"content": [{"type": "text", "text": str(verification)}]}

            elif name == "interaction_search_help_select":
                request = ActionRequest(
                    session_id=arguments["session_id"],
                    action_type="interaction_search_help_select",
                    params={
                        "row": arguments.get("row", 0),
                        "value": arguments.get("value")
                    }
                )
                result = await self.action_dispatcher.execute(request)
                return {"content": [{"type": "text", "text": result.model_dump_json()}]}

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Error executing MCP tool {name}: {str(e)}")
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Error: {str(e)}"}]
            }

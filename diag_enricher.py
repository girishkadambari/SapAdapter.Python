import sys
import os
sys.path.append(r"c:\Users\trainer\Documents\girish-workspace\SapAdapter.Python")
from sap_mcp.observation.enricher import ControlEnricher
from sap_mcp.schemas.control import Control
from sap_mcp.core.config import ControlSubtypes

enricher = ControlEnricher()
control = Control(id="test", type="GuiButton", subtype=ControlSubtypes.BUTTON)
enriched = enricher.enrich(control)
print(f"Enriched actions: {enriched.actions}")
for method in enriched.supported_methods:
    print(f"Method name: {method.name}, Tool: {method.tool}, ActionType: {method.action_type}")

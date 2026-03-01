# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/commands/handlers/modification.py
from loguru import logger
from ...engine.wait_helper import wait_for_idle

async def set_field(session, payload):
    field_id = payload.get("id")
    value = payload.get("value")
    if field_id is None or value is None:
        raise ValueError("id and value required for setField")
        
    logger.info(f"Setting field {field_id} to '{value}'")
    field = session.FindById(field_id)
    field.Text = str(value)
    # Most setField actions don't trigger a roundtrip, but some might. 
    # Usually, we wait for idle after Enter/Button press instead.
    return {"success": True}

async def press_toolbar_button(session, payload):
    button_id = payload.get("id")
    if not button_id:
        raise ValueError("id required for pressToolbarButton")
        
    logger.info(f"Pressing toolbar button: {button_id}")
    # Often buttons are under session.ActiveWindow.ToolbarAction
    # But FindById is more universal for specific button IDs
    button = session.FindById(button_id)
    button.Press()
    await wait_for_idle(session)
    return {"success": True}

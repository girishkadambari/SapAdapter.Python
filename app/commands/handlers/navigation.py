# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/commands/handlers/navigation.py
from loguru import logger
from ...engine.wait_helper import wait_for_idle

async def navigate_tcode(session, payload):
    tcode = payload.get("tcode")
    if not tcode:
        raise ValueError("tcode required")
        
    logger.info(f"Navigating to transaction: {tcode}")
    session.StartTransaction(tcode)
    await wait_for_idle(session)
    return {"success": True}

async def read_field(session, payload):
    field_id = payload.get("id")
    if not field_id:
        raise ValueError("id required")
        
    logger.debug(f"Reading field {field_id}")
    field = session.FindById(field_id)
    return {"value": str(field.Text) if hasattr(field, "Text") else ""}

async def focus_field(session, payload):
    field_id = payload.get("id")
    if not field_id:
        raise ValueError("id required")
        
    logger.debug(f"Focusing field {field_id}")
    field = session.FindById(field_id)
    field.SetFocus()
    return {"success": True}

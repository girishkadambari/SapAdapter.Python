# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/commands/handlers/menu.py
from loguru import logger
from ...engine.wait_helper import wait_for_idle

async def get_menu_paths(session, payload):
    logger.info("MENU_GET_PATHS")
    menu = session.ActiveWindow.MenuBar
    result = []
    items = menu.Children
    for i in range(items.Count):
        top_menu = items.Item(i)
        result.Add(str(top_menu.Text))
    return {"paths": result}

async def select_menu_path(session, payload):
    path = payload.get("path")
    if not path: raise ValueError("path required")
    
    logger.info(f"MENU_SELECT_PATH: {path}")
    menu = session.ActiveWindow.MenuBar
    menu.Select(path)
    await wait_for_idle(session)
    return {"success": True}

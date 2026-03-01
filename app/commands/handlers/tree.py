# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/commands/handlers/tree.py
from loguru import logger
from ...engine.wait_helper import wait_for_idle

async def get_tree_nodes(session, payload):
    shell_id = payload.get("shellId")
    limit = int(payload.get("limit", 50))
    if not shell_id: raise ValueError("shellId required")
    
    logger.info(f"TREE_GET_VISIBLE_NODES: {shell_id} (limit: {limit})")
    tree = session.FindById(shell_id)
    all_keys = tree.GetAllNodeKeys()
    count = min(all_keys.Count, limit)
    
    nodes = []
    for i in range(count):
        key = str(all_keys.Item(i))
        nodes.append({
            "key": key,
            "text": str(tree.GetNodeTextByKey(key)),
            "expanded": bool(tree.IsExpandedByKey(key))
        })
        
    return {"nodes": nodes}

async def find_tree_nodes(session, payload):
    shell_id = payload.get("shellId")
    pattern = payload.get("pattern", "")
    limit = int(payload.get("limit", 10))
    if not shell_id: raise ValueError("shellId required")
    
    logger.info(f"TREE_FIND_NODES: {shell_id} (pattern: {pattern})")
    tree = session.FindById(shell_id)
    all_keys = tree.GetAllNodeKeys()
    
    matches = []
    max_matches = min(limit, 50)
    
    for i in range(all_keys.Count):
        if len(matches) >= max_matches: break
        key = str(all_keys.Item(i))
        text = str(tree.GetNodeTextByKey(key))
        if pattern.lower() in text.lower():
            matches.append({"key": key, "text": text})
            
    return {"matches": matches}

async def select_tree_node(session, payload):
    shell_id = payload.get("shellId")
    path = payload.get("path")
    if not shell_id or not path: raise ValueError("shellId and path required")
    
    logger.info(f"TREE_SELECT_NODE: {shell_id} (path: {path})")
    tree = session.FindById(shell_id)
    tree.SelectNode(path)
    await wait_for_idle(session)
    return {"success": True}

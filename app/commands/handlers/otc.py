# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/commands/handlers/otc.py
import re
from loguru import logger
from ...engine.wait_helper import wait_for_idle

def _parse_sap_number(val):
    try:
        cleaned = re.sub(r'[^\d.,-]', '', val).replace(',', '.')
        return float(cleaned)
    except:
        return 0.0

async def get_sales_order(session, payload):
    sales_order = payload.get("salesOrder")
    if not sales_order: raise ValueError("salesOrder required")
    
    logger.info(f"GET_SALES_ORDER: {sales_order}")
    session.StartTransaction("VA03")
    await wait_for_idle(session)
    
    order_field = session.FindById("wnd[0]/usr/ctxtVBAK-VBELN")
    order_field.Text = str(sales_order)
    session.ActiveWindow.SendVKey(0) # Enter
    await wait_for_idle(session)
    
    net_value = str(session.FindById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBAK-NETWR").Text)
    delivery_block = str(session.FindById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/ctxtVBAK-LIFSK").Text)
    status_bar = str(session.ActiveWindow.StatusBar.Text)
    
    return {
        "success": True,
        "data": {
            "salesOrder": sales_order,
            "status": status_bar if status_bar else "Loaded",
            "netValue": net_value.strip(),
            "deliveryBlock": delivery_block.strip()
        }
    }

async def check_credit_limit(session, payload):
    customer = payload.get("customer")
    if not customer: raise ValueError("customer required")
    
    logger.info(f"CHECK_CREDIT_LIMIT: {customer}")
    session.StartTransaction("FD32")
    await wait_for_idle(session)
    
    session.FindById("wnd[0]/usr/ctxtRF02L-KUNNR").Text = str(customer)
    session.FindById("wnd[0]/usr/chkRF02L-D0110").Selected = True
    session.ActiveWindow.SendVKey(0) # Enter
    await wait_for_idle(session)

    # Detect S/4HANA Obsolescence Popup (SAP Note 1946054)
    try:
        if session.ActiveWindow.Type == "GuiModalWindow" and "Note 1946054" in session.ActiveWindow.Text:
            logger.warning(f"FD32 is obsolete in this system. Directing user to UKM_BP.")
            session.ActiveWindow.Close()
            return {
                "success": False,
                "error": "TCODE_OBSOLETE",
                "message": "FD32 is obsolete in S/4HANA. Use UKM_BP for Credit Management.",
                "sapNote": "1946054"
            }
    except:
        pass
    
    limit = str(session.FindById("wnd[0]/usr/txtKNKK-KLTOL").Text)
    exposure = str(session.FindById("wnd[0]/usr/txtRF02L-SAKNR").Text)
    risk = str(session.FindById("wnd[0]/usr/ctxtKNKK-CTLPC").Text)
    
    return {
        "success": True,
        "data": {
            "creditLimit": _parse_sap_number(limit),
            "currentExposure": _parse_sap_number(exposure),
            "riskCategory": risk.strip()
        }
    }

async def get_receivables(session, payload):
    customer = payload.get("customer")
    if not customer: raise ValueError("customer required")
    
    logger.info(f"GET_RECEIVABLES: {customer}")
    session.StartTransaction("FBL5N")
    await wait_for_idle(session)
    
    session.FindById("wnd[0]/usr/ctxtDD_KUNNR-LOW").Text = str(customer)
    session.FindById("wnd[0]/usr/radX_OPENT").Select()
    session.ActiveWindow.SendVKey(8) # F8
    await wait_for_idle(session)
    
    grid = session.FindById("wnd[0]/usr/cntlGRID1/shellcont/shell")
    row_count = int(grid.RowCount)
    
    items = []
    for i in range(min(row_count, 10)):
        items.append({
            "amount": str(grid.GetCellValue(i, "WRBTR")),
            "dueDate": str(grid.GetCellValue(i, "FAEDT")),
            "document": str(grid.GetCellValue(i, "BELNR"))
        })
        
    return {"success": True, "data": {"items": items}}

async def navigate_credit_release(session, payload):
    sales_order = str(payload.get("salesOrder"))
    if not sales_order: raise ValueError("salesOrder required")
    
    logger.info(f"NAVIGATE_CREDIT_RELEASE: {sales_order}")
    session.StartTransaction("VKM3")
    await wait_for_idle(session)
    session.ActiveWindow.SendVKey(8) # F8
    await wait_for_idle(session)
    
    grid = session.FindById("wnd[0]/usr/cntlGRID1/shellcont/shell")
    row_count = int(grid.RowCount)
    found_row = -1
    
    for i in range(row_count):
        if str(grid.GetCellValue(i, "VBELN")) == sales_order:
            found_row = i
            break
            
    if found_row == -1:
        return {"success": False, "error": f"Sales order {sales_order} not found in VKM3"}
        
    grid.SelectedRows = str(found_row)
    return {"success": True, "target": "VKM3", "salesOrder": sales_order, "rowIndex": found_row}

async def release_credit_block(session, payload):
    logger.info("RELEASE_CREDIT_BLOCK")
    session.FindById("wnd[0]/tbar[1]/btn[24]").Press()
    await wait_for_idle(session)
    session.ActiveWindow.SendVKey(11) # Save
    await wait_for_idle(session)
    return {"success": True}

async def open_po_display(session, payload):
    po_id = payload.get("poId", "")
    logger.info(f"OPEN_PO_DISPLAY: {po_id}")
    session.StartTransaction("ME23N")
    await wait_for_idle(session)
    return {"success": True, "target": "ME23N", "poId": po_id}

async def open_po_history(session, payload):
    shell_id = payload.get("shellId")
    row_index = int(payload.get("rowIndex", 0))
    if not shell_id: raise ValueError("shellId required")
    
    logger.info(f"OPEN_PO_HISTORY: {shell_id} row {row_index}")
    grid = session.FindById(shell_id)
    grid.SetCurrentCell(row_index, "EBELP")
    return {"success": True, "action": "PO_HISTORY_TRIGGERED"}

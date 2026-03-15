from typing import Any, Optional, List
from loguru import logger
from ..schemas.observation import Modal

class ModalGuard:
    """
    Detects and analyzes modal dialogs blocking the main window for autonomous agents.
    """
    
    @staticmethod
    def detect(session: Any) -> Optional[Modal]:
        """Returns info about the active modal window if one exists."""
        try:
            active_win = session.ActiveWindow
            if active_win and active_win.Type == "GuiModalWindow":
                buttons = ModalGuard._extract_buttons(active_win)
                text = ModalGuard._extract_modal_text(active_win)
                title = str(active_win.Text)
                
                return Modal(
                    id=str(active_win.Id),
                    title=title,
                    text=text,
                    buttons=buttons,
                    category=ModalGuard._classify(title, text, buttons)
                )
            
            if hasattr(session.Info, "Status") and session.Info.Status == 1:
                return Modal(
                    id="unknown",
                    title="Unknown Modal",
                    text="A modal dialog is blocking interaction.",
                    category="SYSTEM"
                )
                
            return None
        except Exception as e:
            logger.debug(f"Modal detection failed: {str(e)}")
            return None

    @staticmethod
    def _classify(title: str, text: str, buttons: List[str]) -> str:
        t = (title + " " + text).upper()
        if any(w in t for w in ["SAVE", "DELETE", "CANCEL", "CHOOSE", "SELECT"]):
            return "CONFIRMATION"
        if any(w in t for w in ["ENTER", "REQUIRED", "INVALID", "FILL"]):
            return "INSTRUCTIONAL"
        return "SYSTEM"

    @staticmethod
    def _extract_buttons(window: Any) -> List[str]:
        buttons = []
        try:
            def _find_btns(container):
                for i in range(container.Children.Count):
                    child = container.Children(i)
                    if child.Type == "GuiButton":
                        buttons.append(str(child.Text) or str(child.Name))
                    if hasattr(child, "Children"):
                        _find_btns(child)
            _find_btns(window)
        except: pass
        return buttons

    @staticmethod
    def _extract_modal_text(window: Any) -> str:
        texts = []
        try:
            def _find_text(container):
                for i in range(container.Children.Count):
                    child = container.Children(i)
                    if child.Type == "GuiLabel":
                        texts.append(str(child.Text))
                    elif child.Type == "GuiTextField" and not child.Changeable:
                        texts.append(str(child.Text))
                    if hasattr(child, "Children"):
                        _find_text(child)
            _find_text(window)
        except: pass
        return " ".join(texts)

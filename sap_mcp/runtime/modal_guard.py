from typing import Any, Optional
from loguru import logger
from ..schemas.observation import Modal

class ModalGuard:
    """
    Detects and analyzes modal dialogs blocking the main window.
    """
    
    @staticmethod
    def detect(session: Any) -> Optional[Modal]:
        """
        Returns info about the active modal window if one exists.
        """
        try:
            # SAP GUI scripting: Window type 1 is usually a modal
            # session.Children contains all windows. Children(0) is usually main window.
            # But session.ActiveWindow is simpler.
            active_win = session.ActiveWindow
            if active_win and active_win.Type == "GuiModalWindow":
                return Modal(
                    id=str(active_win.Id),
                    title=str(active_win.Text),
                    text=ModalGuard._extract_modal_text(active_win)
                )
            
            # Additional check: session.Info.Status == 1 often indicates modal
            if hasattr(session.Info, "Status") and session.Info.Status == 1:
                return Modal(
                    id="unknown",
                    title="Unknown Modal",
                    text="A modal dialog is blocking interaction but window details are inaccessible."
                )
                
            return None
        except Exception as e:
            logger.debug(f"Modal detection failed: {str(e)}")
            return None

    @staticmethod
    def _extract_modal_text(window: Any) -> str:
        """
        Attempts to extract descriptive text from a modal dialog.
        """
        try:
            # Look for labels or messages in the modal
            texts = []
            def _find_text(container):
                for i in range(container.Children.Count):
                    child = container.Children(i)
                    if child.Type == "GuiLabel":
                        texts.append(child.Text)
                    if hasattr(child, "Children"):
                        _find_text(child)
            
            _find_text(window)
            return " ".join(texts)
        except:
            return ""

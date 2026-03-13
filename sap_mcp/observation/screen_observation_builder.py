from typing import Any, Optional
from datetime import datetime, timezone
from ..schemas.observation import ScreenObservation, StatusBar, Modal, ValidationSummary
from ..runtime.sap_runtime import SapRuntime
from .raw_snapshot_builder import RawSnapshotBuilder
from .normalized_snapshot_builder import NormalizedSnapshotBuilder
from ..snapshot.screenshot_service import ScreenshotService
from ..classification.screen_classifier import ScreenClassifier

class ScreenObservationBuilder:
    """
    Coordinates the capture of a full ScreenObservation.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime
        self.raw_builder = RawSnapshotBuilder()
        self.norm_builder = NormalizedSnapshotBuilder()
        self.screenshot_service = ScreenshotService()
        self.classifier = ScreenClassifier()

    async def build(self, session_id: Optional[str] = None, include_screenshot: bool = False) -> ScreenObservation:
        """
        Main entry point to capture the current state.
        """
        session = self.runtime.get_session(session_id)
        
        # 1. Base Info
        info = session.Info
        win = session.ActiveWindow
        
        # 2. Status Bar
        sb_model = self._capture_status_bar(session)
        
        # 3. Modal Check
        modal_model = self.runtime.modal_guard.detect(session)
        
        # 4. Controls
        raw_controls = self.raw_builder.capture(win)
        norm_controls = [self.norm_builder.normalize_control(r) for r in raw_controls]

        # 5. Classification
        title = str(win.Text) if win else "SAP"
        screen_type = self.classifier.classify(norm_controls, title)
        metadata = self.classifier.get_metadata(norm_controls, screen_type)

        # 6. Screenshot (Optional)
        screenshot_data = None
        if include_screenshot:
            try:
                # We need the HWND of the ActiveWindow
                # In SAP GUI, the window handle is often accessible via win.Handle
                hwnd = getattr(win, "Handle", 0)
                if hwnd:
                    img = self.screenshot_service.capture_window(int(hwnd))
                    if img:
                        screenshot_data = self.screenshot_service.to_base64(img)
            except Exception as e:
                logger.warning(f"Failed to capture screenshot during observation: {str(e)}")

        return ScreenObservation(
            session_id=str(session_id or self.runtime.session_manager.active_session_id),
            transaction=str(info.Transaction),
            title=title,
            program=str(info.Program),
            status_bar=sb_model,
            modal=modal_model,
            controls=norm_controls,
            screen_type=str(screen_type.value if hasattr(screen_type, "value") else screen_type),
            metadata=metadata,
            screenshot_data=screenshot_data,
            validation_summary=ValidationSummary(is_valid=True)
        )

    def _capture_status_bar(self, session: Any) -> StatusBar:
        try:
            sb = session.ActiveWindow.StatusBar
            m_type = str(sb.MessageType)
            if m_type == "None": m_type = ""
            
            return StatusBar(
                type=m_type,
                text=str(sb.Text),
                msg_id=str(getattr(sb, "MessageId", None)),
                msg_no=str(getattr(sb, "MessageNumber", None))
            )
        except:
            return StatusBar(type="", text="")

from typing import Any, Optional, Dict, List
from loguru import logger

from ..schemas.observation import ScreenObservation, StatusBar, Modal, ValidationSummary
from ..runtime.sap_runtime import SapRuntime
from .raw_snapshot_builder import RawSnapshotBuilder
from .extractors.registry import ExtractorRegistry
from .enricher import ControlEnricher
from ..snapshot.screenshot_service import ScreenshotService
from ..classification.screen_classifier import ScreenClassifier
from .tree_processor import TreeProcessor

class ScreenObservationBuilder:
    """
    Coordinates the capture of a full ScreenObservation.
    Orchestrates identification, extraction, enrichment, and classification.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime
        self.raw_builder = RawSnapshotBuilder()
        self.extractor_registry = ExtractorRegistry()
        self.enricher = ControlEnricher()
        self.screenshot_service = ScreenshotService()
        self.classifier = ScreenClassifier()
        self.tree_processor = TreeProcessor()

    async def build(
        self, 
        session_id: Optional[str] = None, 
        include_screenshot: bool = False, 
        mode: str = "FULL",
        target_id: Optional[str] = None
    ) -> ScreenObservation:
        """
        Main entry point to capture the current state.
        """
        session = self.runtime.get_session(session_id)
        win = session.ActiveWindow
        
        # 1. Base Info (StatusBar, Modal)
        sb_model = self._capture_status_bar(session)
        modal_model = self.runtime.modal_guard.detect(session)
        
        # 2. Control Collection
        controls = await self._collect_controls(session, mode, target_id)

        # 3. Enrichment (Adds actions, supported methods)
        controls = [self.enricher.enrich(c) for c in controls]

        # 4. Mode-based filtering
        if mode == "SUMMARY":
            controls = [
                c for c in controls 
                if c.visible and (c.editable or c.subtype in ("button", "tab", "combobox", "statusbar"))
            ]

        # 5. Classification & Metadata
        title = str(win.Text) if win else "SAP"
        screen_type = self.classifier.classify(controls, title)
        metadata = self.classifier.get_metadata(controls, screen_type)

        # 6. Screenshot
        screenshot_data = None
        if include_screenshot:
            screenshot_data = self._capture_screenshot(win)

        return ScreenObservation(
            session_id=str(session_id or self.runtime.session_manager.active_session_id),
            transaction=str(session.Info.Transaction),
            title=title,
            program=str(session.Info.Program),
            program_name=str(session.Info.Program),
            dynpro_number=str(session.Info.ScreenNumber),
            status_bar=sb_model,
            modal=modal_model,
            controls=controls,
            screen_type=str(screen_type.value if hasattr(screen_type, "value") else screen_type),
            metadata=metadata,
            screenshot_data=screenshot_data,
            validation_summary=ValidationSummary(is_valid=True)
        )

    async def _collect_controls(self, session: Any, mode: str, target_id: Optional[str]) -> List[Any]:
        """
        Collects controls using the optimized GetObjectTree batch API.
        """
        if mode == "FOCUSED" and target_id:
            logger.warning("FOCUSED mode is deprecated and uses GetObjectTree for full capture instead.")

        try:
            raw_snapshot = self.raw_builder.get_raw_snapshot(session)
            return self.tree_processor.process_json_tree(raw_snapshot["optimized_tree"])
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return []

    def _capture_status_bar(self, session: Any) -> StatusBar:
        try:
            sb = session.ActiveWindow.StatusBar
            return StatusBar(
                type=str(sb.MessageType).replace("None", ""),
                text=str(sb.Text),
                msg_id=str(getattr(sb, "MessageId", None)),
                msg_no=str(getattr(sb, "MessageNumber", None))
            )
        except:
            return StatusBar(type="", text="")

    def _capture_screenshot(self, win: Any) -> Optional[str]:
        try:
            hwnd = getattr(win, "Handle", 0)
            if hwnd:
                img = self.screenshot_service.capture_window(int(hwnd))
                return self.screenshot_service.to_base64(img)
        except Exception as e:
            logger.warning(f"Screenshot failed: {e}")
        return None

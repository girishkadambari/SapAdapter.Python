from typing import Any, Optional, Dict, List
from datetime import datetime, timezone
from loguru import logger

from ..schemas.observation import ScreenObservation, StatusBar, Modal, ValidationSummary
from ..runtime.sap_runtime import SapRuntime
from .raw_snapshot_builder import RawSnapshotBuilder
from .extractors.registry import ExtractorRegistry
from .enricher import ControlEnricher
from ..snapshot.screenshot_service import ScreenshotService
from ..classification.screen_classifier import ScreenClassifier
from ..core.config import ControlSubtypes

class ScreenObservationBuilder:
    """
    Coordinates the capture of a full ScreenObservation.
    Refactored to orchestrate Extractors and Enrichers following Phase 2 LLD.
    """
    
    def __init__(self, runtime: SapRuntime):
        self.runtime = runtime
        self.raw_builder = RawSnapshotBuilder()
        self.extractor_registry = ExtractorRegistry()
        self.enricher = ControlEnricher()
        self.screenshot_service = ScreenshotService()
        self.classifier = ScreenClassifier()

    async def build(
        self, 
        session_id: Optional[str] = None, 
        include_screenshot: bool = False, 
        mode: str = "FULL",
        target_id: Optional[str] = None
    ) -> ScreenObservation:
        """
        Main entry point to capture the current state.
        Orchestrates identification, extraction, enrichment, and classification.
        """
        session = self.runtime.get_session(session_id)
        win = session.ActiveWindow
        
        # 1. Base Info (StatusBar, Modal)
        sb_model = self._capture_status_bar(session)
        modal_model = self.runtime.modal_guard.detect(session)
        
        # 2. Control Collection
        controls = []
        if mode == "FOCUSED" and target_id:
            try:
                control_obj = session.FindById(target_id)
                controls = self._process_controls([control_obj])
            except Exception as e:
                logger.warning(f"Focused extraction failed for {target_id}: {str(e)}")
        else:
            # Capture hierarchy
            raw_com_objects = self._get_com_objects(session)
            controls = self._process_controls(raw_com_objects)

            # Mode-based filtering
            if mode == "SUMMARY":
                # Filter to only relevant interactive controls
                controls = [
                    c for c in controls 
                    if c.visible and (c.editable or c.subtype in ("button", "tab", "combobox", "statusbar"))
                ]

        # 3. Classification & Metadata
        title = str(win.Text) if win else "SAP"
        screen_type = self.classifier.classify(controls, title)
        metadata = self.classifier.get_metadata(controls, screen_type)

        # 4. Screenshot
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

    def _process_controls(self, com_objects: List[Any]) -> List[Any]:
        """
        Pipelines COM objects through Extraction and Enrichment.
        """
        processed = []
        for obj in com_objects:
            extractor = self.extractor_registry.get_extractor(obj)
            if extractor:
                control = extractor.extract(obj)
                control = self.enricher.enrich(control)
                processed.append(control)
        return processed

    def _get_com_objects(self, session: Any) -> List[Any]:
        """
        Retrieves raw COM objects from the session.
        Uses RawSnapshotBuilder but returns objects instead of dicts.
        """
        # Note: We need to modify RawSnapshotBuilder to return COM objects 
        # or handle the logic here directly. For now, we'll use a simplified recursive scan.
        objects = []
        
        def scan(component):
            objects.append(component)
            if hasattr(component, "Children"):
                children = component.Children
                if children is not None:
                    for i in range(children.Count):
                        scan(children(i))
                    
        scan(session)
        return objects

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

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

    async def build(
        self, 
        session_id: Optional[str] = None, 
        include_screenshot: bool = False, 
        force_recursive: bool = False,
        mode: str = "FULL",
        target_id: Optional[str] = None
    ) -> ScreenObservation:
        """
        Main entry point to capture the current state.
        Supported modes: FULL, SUMMARY, FOCUSED.
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
        if mode == "FOCUSED" and target_id:
            # Targeted extraction for a single control
            try:
                control_obj = session.FindById(target_id)
                raw_snapshot = self.raw_builder._extract_properties(control_obj)
                norm_controls = [self.norm_builder.normalize_control(raw_snapshot)]
            except Exception as e:
                logger.warning(f"Focused extraction failed for {target_id}: {str(e)}")
                norm_controls = []
        else:
            raw_snapshot = self.raw_builder.get_raw_snapshot(session)
            
            if raw_snapshot.get("is_optimized"):
                norm_controls = self.norm_builder.normalize_optimized_tree(raw_snapshot["optimized_tree"])
            else:
                all_raw = [raw_snapshot] + raw_snapshot.get("children", [])
                norm_controls = [self.norm_builder.normalize_control(r) for r in all_raw]

            # Mode-based filtering
            if mode == "SUMMARY":
                # Primary filter: Editable fields, key UI elements, and non-empty status bars
                norm_controls = [
                    c for c in norm_controls 
                    if c.editable or c.subtype in ("button", "tab", "combobox", "statusbar")
                ]
                
                # Secondary filter: Remove "junk" layout containers or invisible buttons
                norm_controls = [c for c in norm_controls if c.visible]
                
                # Context enrichment: Add semantic hints to controls
                for c in norm_controls:
                    if not c.label and c.id:
                        # Extract potential semantic name from ID (e.g. txtRSYST-BNAME -> BNAME)
                        parts = c.id.split("-")
                        if len(parts) > 1:
                            hint = parts[-1].lower()
                            c.metadata["semantic_hint"] = hint
                            # If label is truly empty, use hint as fallback
                            if not c.label:
                                c.label = hint.replace("_", " ").title()

        # 5. Classification
        title = str(win.Text) if win else "SAP"
        screen_type = self.classifier.classify(norm_controls, title)
        metadata = self.classifier.get_metadata(norm_controls, screen_type)

        # 6. Screenshot (Optional)
        screenshot_data = None
        if include_screenshot:
            try:
                hwnd = getattr(win, "Handle", 0)
                if hwnd:
                    img = self.screenshot_service.capture_window(int(hwnd))
                    if img:
                        screenshot_data = self.screenshot_service.to_base64(img)
            except Exception as e:
                logger.warning(f"Failed to capture screenshot during observation: {str(e)}")

        # Verification context mapping:
        # Help the agent know which tool to use for which control
        for c in norm_controls:
            if c.editable:
                if c.subtype == "combobox":
                    c.actions.append("sap_interact_field:set_field (via key)")
                elif c.subtype == "table":
                    c.actions.extend([
                        "sap_table_action:set_cell_data",
                        "sap_table_action:table_select_row",
                        "sap_table_action:table_double_click_row",
                        "sap_table_action:read_table_rows"
                    ])
                else:
                    c.actions.append("sap_interact_field:set_field")
            elif c.subtype == "button":
                c.actions.append("sap_press_button")

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

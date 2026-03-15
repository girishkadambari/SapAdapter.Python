from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ...schemas.control import Control

class BaseControlExtractor(ABC):
    """
    Abstract base class for all SAP control extractors.
    Focuses EXCLUSIVELY on property extraction from COM objects.
    """
    
    @abstractmethod
    def identify(self, control: Any) -> bool:
        """
        Returns True if this extractor can handle the given SAP control.
        """
        pass

    @abstractmethod
    def extract(self, control: Any) -> Control:
        """
        Extracts structured data from the SAP control into a canonical Control model.
        """
        pass

    def normalize_id(self, raw_id: str) -> str:
        """
        Normalizes a SAP GUI ID by removing the session prefix.
        """
        if "/wnd[" in raw_id:
            return "wnd[" + raw_id.split("/wnd[")[-1]
        return raw_id

    def get_basic_props(self, control: Any) -> Dict[str, Any]:
        """
        Helper to extract common properties from any GuiComponent.
        """
        return {
            "id": self.normalize_id(str(control.Id)),
            "type": str(control.Type),
            "text": str(getattr(control, "Text", "")) if hasattr(control, "Text") else None,
            "tooltip": str(getattr(control, "Tooltip", "")) if hasattr(control, "Tooltip") else None,
            "changeable": bool(getattr(control, "Changeable", False)),
            "visible": bool(getattr(control, "Visible", True)),
            "parent_id": self.normalize_id(str(control.Parent.Id)) if control.Parent else None,
        }

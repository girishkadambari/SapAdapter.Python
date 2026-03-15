from typing import Any, Dict, List, Type
from .base_extractor import BaseControlExtractor
from .button_extractor import ButtonExtractor
from .field_extractor import FieldExtractor
from .table_extractor import TableExtractor
from .grid_extractor import GridExtractor
from .tree_extractor import TreeExtractor
from .tab_extractor import TabExtractor
from loguru import logger

class ExtractorRegistry:
    """
    Registry for hardware-specific property extractors.
    Refactored to support SRP by separating identification from extraction.
    """
    
    def __init__(self):
        self._extractors: List[BaseControlExtractor] = [
            ButtonExtractor(),
            FieldExtractor(),
            TableExtractor(),
            GridExtractor(),
            TreeExtractor(),
            TabExtractor()
            # Add others as needed (Shell, Menu, etc.)
        ]

    def get_extractor(self, control: Any) -> BaseControlExtractor:
        """
        Finds the first extractor that identifies the control.
        """
        for extractor in self._extractors:
            if extractor.identify(control):
                return extractor
        return None

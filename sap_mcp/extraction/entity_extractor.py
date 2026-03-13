from typing import Any, Dict, List, Optional
from ..schemas.extraction import BusinessExtraction
from ..schemas.observation import ScreenObservation
from .form_extractor import FormExtractor

class EntityExtractor:
    """
    Service to map raw data into domain entities (e.g., Sales Order).
    """
    
    def __init__(self):
        self.form_extractor = FormExtractor()

    def extract_entity(self, observation: ScreenObservation, entity_type: str) -> BusinessExtraction:
        """
        High-level extraction for a specific business entity.
        """
        form_data = self.form_extractor.extract_form_data(observation)
        
        # Generic mapping logic (could be extended with templates)
        extracted_data = {}
        source_controls = []
        
        # This is a basic implementation. Future versions could use 
        # semantic matching or domain-specific field maps.
        for label, value in form_data.items():
            # Example: map "Order" label to "order_id" key
            key = label.lower().replace(" ", "_")
            extracted_data[key] = value
            
        return BusinessExtraction(
            entity_type=entity_type,
            data=extracted_data,
            source_controls=[c.id for c in observation.controls if c.value in extracted_data.values()],
            completeness="Partial",
            confidence=0.8
        )

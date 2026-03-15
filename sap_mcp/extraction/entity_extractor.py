from typing import Any, Dict, List, Optional
from ..schemas.extraction import BusinessExtraction
from ..schemas.observation import ScreenObservation
from .form_extractor import FormExtractor

class EntityExtractor:
    """
    Service to map raw data into domain entities (e.g., Sales Order).
    Refactored to use a template-driven approach for better LLD.
    """
    
    # Templates could eventually move to Config or external JSON
    TEMPLATES = {
        "SalesOrder": {
            "vbeln": ["Order", "Sales Document", "Document Number"],
            "kunnr": ["Sold-To Party", "Customer", "Customer No."],
            "vkorg": ["Sales Organization", "Sales Org."],
            "vtweg": ["Distribution Channel", "Distr. Channel"]
        },
        "PurchaseOrder": {
            "ebeln": ["Purchasing Document", "PO Number"],
            "lifnr": ["Vendor", "Supplier"]
        }
    }
    
    def __init__(self):
        self.form_extractor = FormExtractor()

    def extract_entity(self, observation: ScreenObservation, entity_type: str) -> BusinessExtraction:
        """
        High-level extraction for a specific business entity using templates.
        """
        form_data = self.form_extractor.extract_form_data(observation)
        template = self.TEMPLATES.get(entity_type, {})
        
        extracted_data = {}
        for key, aliases in template.items():
            # Try to match aliases in form data
            for alias in aliases:
                if alias in form_data:
                    extracted_data[key] = form_data[alias]
                    break
        
        # Fallback to generic mapping if no template or partial match
        if not extracted_data:
            for label, value in form_data.items():
                key = label.lower().replace(" ", "_")
                extracted_data[key] = value
            
        return BusinessExtraction(
            entity_type=entity_type,
            data=extracted_data,
            source_controls=[c.id for c in observation.controls if c.value in extracted_data.values()],
            completeness="Complete" if len(extracted_data) >= len(template) else "Partial",
            confidence=0.9 if extracted_data else 0.5
        )

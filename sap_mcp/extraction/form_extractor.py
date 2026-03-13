from typing import List, Dict, Optional, Tuple
from ..schemas.control import Control
from ..schemas.observation import ScreenObservation

class FormExtractor:
    """
    Service to extract logical forms and field-label mappings from screen observations.
    """
    
    def extract_form_data(self, observation: ScreenObservation) -> Dict[str, str]:
        """
        Returns a mapping of label -> value for all identified fields on the screen.
        """
        form_data = {}
        controls = observation.controls
        
        # 1. Map labels to their nearest fields
        labels = [c for c in controls if c.subtype == "label"]
        fields = [c for c in controls if c.subtype in ["text", "checkbox", "radio", "combobox"]]
        
        for field in fields:
            label_text = self._find_label_for_field(field, labels)
            if label_text:
                form_data[label_text] = field.value
            else:
                # Fallback to technical ID if no label found
                form_data[field.id] = field.value
                
        return form_data

    def _find_label_for_field(self, field: Control, labels: List[Control]) -> Optional[str]:
        """
        Heuristic-based label matching (e.g., label to the left or above).
        """
        if field.label:
            return field.label
            
        # If no explicit label, try spatial proximity
        if not field.bounds:
            return None
            
        fx, fy, fw, fh = field.bounds
        best_label = None
        min_dist = float('inf')
        
        for label in labels:
            if not label.bounds or not label.value:
                continue
                
            lx, ly, lw, lh = label.bounds
            
            # Check if label is to the left (common in SAP)
            if abs(ly - fy) < 10 and lx < fx:
                dist = fx - (lx + lw)
                if dist < min_dist:
                    min_dist = dist
                    best_label = label.value
                    
        return best_label

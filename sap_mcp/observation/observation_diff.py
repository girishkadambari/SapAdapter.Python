from typing import List, Dict, Any
from ..schemas.observation import ScreenObservation

class ObservationDiff:
    """
    Calculates differences between two ScreenObservations.
    """
    
    def compare(self, old: ScreenObservation, new: ScreenObservation) -> Dict[str, Any]:
        """
        Returns a summary of changes.
        """
        diff = {
            "screen_changed": old.transaction != new.transaction or old.title != new.title,
            "status_changed": old.status_bar.text != new.status_bar.text,
            "changed_controls": [],
            "new_controls": [],
            "removed_controls": []
        }
        
        old_map = {c.id: c for c in old.controls}
        new_map = {c.id: c for c in new.controls}
        
        for cid, control in new_map.items():
            if cid not in old_map:
                diff["new_controls"].append(cid)
            elif old_map[cid].value != control.value:
                diff["changed_controls"].append({
                    "id": cid,
                    "old_value": old_map[cid].value,
                    "new_value": control.value
                })
                
        for cid in old_map:
            if cid not in new_map:
                diff["removed_controls"].append(cid)
                
        return diff

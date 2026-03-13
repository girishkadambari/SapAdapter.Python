from typing import Any, Dict, List
from pydantic import BaseModel, Field

class BusinessExtraction(BaseModel):
    """
    Represents business-oriented data extracted from a SAP screen.
    """
    entity_type: str = Field(..., description="Type of business entity (e.g., SalesOrder, PurchaseOrder, Customer)")
    data: Dict[str, Any] = Field(..., description="The extracted data fields")
    source_controls: List[str] = Field(default_factory=list, description="List of control IDs used to extract this data")
    completeness: str = Field("Partial", description="Whether the extraction is Full or Partial")
    confidence: float = Field(..., description="Confidence score for the extraction accuracy")

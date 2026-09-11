"""
AgriSmart AI - Disease Diagnosis & Cureness Pydantic Schemas
Supports Dual-Model pipeline: Model 1 (Detection) + Model 2 (Cureness).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PathPredictionRequest(BaseModel):
    """Payload for judges / automated scripts calling prediction by path"""
    image_path: str = Field(..., description="Local path to the leaf image file to evaluate")


class PathPredictionResponse(BaseModel):
    """Direct response format matching Section 4.1 submission contract"""
    class_label: str = Field(..., description="Predicted class name from the shared list")


class ProbabilityItem(BaseModel):
    class_name: str = Field(..., alias="class")
    probability: float

    class Config:
        populate_by_name = True


class CurenessPlan(BaseModel):
    """Model 2: Agronomic Cureness & Treatment Plan"""
    cureness_score: float
    recovery_chance_pct: float
    recovery_timeline: str
    recovery_timeline_days: int
    urgency_level: str
    prognosis_summary: str
    phases: Dict[str, str]
    dosage_guide: Dict[str, str]
    model_type: str = "Model_2_Cureness_Prescriber"


class DiseasePredictionResponse(BaseModel):
    """Farmer-friendly detailed disease detection & cureness response"""
    predicted_class: str
    confidence: float
    is_healthy: bool
    crop: str
    disease_name: str
    severity: str
    top_k: List[ProbabilityItem]
    
    # Model 2 Enriched Cureness Plan
    cureness_plan: Optional[CurenessPlan] = None
    
    # Direct access convenience fields
    recovery_chance_pct: Optional[float] = None
    recovery_timeline: Optional[str] = None
    urgency_level: Optional[str] = None
    precaution: str
    organic_remedy: Optional[str] = None
    chemical_remedy: Optional[str] = None
    
    image_filename: Optional[str] = None
    saved_record_id: Optional[int] = None
    architecture: str = "Dual_AI_Engine (Model 1: Disease + Model 2: Cureness)"

    class Config:
        from_attributes = True


class DirectCureRequest(BaseModel):
    """Request payload to query Model 2 directly for a known disease"""
    disease_class: str = Field(..., description="Name of the disease (e.g., 'Tomato Early Blight')")
    crop: Optional[str] = Field(None, description="Crop name if known")
    growth_stage: Optional[str] = Field("Growing", description="Current growth stage of crop")


class ClassInfo(BaseModel):
    class_name: str
    crop: str
    disease_name: str
    is_healthy: bool
    severity: str
    precaution: str


class CatalogResponse(BaseModel):
    total_classes: int
    classes: List[ClassInfo]

"""
AgriSmart AI - Disease Diagnosis & Gemini Pro Advisory Schemas
Integrates Computer Vision Detection with Gemini Pro conversational cure advisory.
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


class DiseaseDescriptionInfo(BaseModel):
    """Groq LLM generated disease description and cure consultation prompt"""
    disease_name: str
    crop: str
    status: str
    severity: Optional[str] = None  # May be absent for healthy plants
    description: str = Field(..., description="AI explanation of the disease and its impact on yield")
    follow_up_prompt: str = Field(..., description="Prompt asking if the farmer wants a cure plan")
    requires_cure: bool
    ai_provider: str


class GeminiCurePlan(BaseModel):
    """Groq LLM generated step-by-step cure and recovery plan"""
    disease_name: str
    crop: str
    recovery_chance_pct: float = Field(..., description="Probability of recovery with immediate treatment")
    recovery_timeline: str = Field(..., description="Estimated timeline to recover")
    urgency_level: str = Field(..., description="Urgency of action required")
    containment_action: Optional[str] = None
    organic_treatment: str = Field(..., description="Organic remedy formulation and dosage")
    chemical_treatment: str = Field(..., description="Chemical fungicide/bactericide and dosage")
    cultural_management: Optional[str] = None
    prognosis_summary: Optional[str] = None
    ai_provider: str


class DiseasePredictionResponse(BaseModel):
    """Complete response: CV Detection + Groq Description + Cure Prompt"""
    predicted_class: str
    confidence: float
    is_healthy: bool
    crop: str
    disease_name: str
    severity: str
    top_k: List[ProbabilityItem]  # Up to top-5 predictions

    # Groq Generative Advisory
    disease_description: DiseaseDescriptionInfo
    cure_plan: Optional[GeminiCurePlan] = Field(
        None,
        description="Populated if the farmer confirms they want a cure (include_cure=True) or calls /cure"
    )

    image_filename: Optional[str] = None
    saved_record_id: Optional[int] = None
    architecture: str = "DenseNet-201 (EMA + TTA) + Groq LLM Advisory"
    tta_enabled: Optional[bool] = None
    temperature: Optional[float] = None

    class Config:
        from_attributes = True


class CureRequest(BaseModel):
    """Payload to request a Gemini Pro cure plan for a known disease"""
    disease_class: str = Field(..., description="Name of the disease (e.g., 'Tomato Early Blight')")
    crop: Optional[str] = Field("Tomato", description="Crop name")
    growth_stage: Optional[str] = Field("Growing", description="Current growth stage of crop")
    language: Optional[str] = Field("en", description="Preferred response language (en, hi, mr, etc.)")


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

"""
AgriSmart AI - Advisory & Agentic System Schemas
Covers Bonus C (Weather), Bonus B (Irrigation), and Bonus G (Agentic Advisor)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ── Weather Schemas (Bonus C) ──
class CurrentWeatherInfo(BaseModel):
    temperature: float
    humidity: int
    wind_speed: float
    precipitation: float
    condition: str
    icon: str


class IrrigationWeatherAction(BaseModel):
    badge: str
    title: str
    detail: str
    delay_recommended: bool
    rain_24h_mm: float
    prob_24h_pct: int
    rain_48h_mm: float


class SprayWindowInfo(BaseModel):
    status: str
    badge_color: str
    title: str
    reason: str
    wind_speed_kmh: float


class DiseaseRiskInfo(BaseModel):
    level: str
    score: int
    badge_color: str
    advice: str
    favorable_humidity_hours: int


class ForecastDayItem(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    rain_sum_mm: float
    rain_prob_pct: int
    condition: str
    icon: str


class WeatherIntelligenceResponse(BaseModel):
    current: CurrentWeatherInfo
    irrigation_action: IrrigationWeatherAction
    spray_window: SprayWindowInfo
    disease_risk: DiseaseRiskInfo
    forecast_days: List[ForecastDayItem]
    data_source: str
    location: Dict[str, float]


# ── Irrigation Schemas (Bonus B) ──
class IrrigationRequest(BaseModel):
    crop: str = Field("Tomato", description="Crop name (e.g. Tomato, Potato, Corn)")
    growth_stage: str = Field("Flowering", description="Crop stage: Vegetative, Flowering, Fruiting, Maturity")
    soil_moisture_pct: float = Field(..., ge=0, le=100, description="Soil moisture level percentage (0-100)")
    soil_type: str = Field("Loamy", description="Soil texture: Loamy, Clay, Sandy")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class IrrigationResponse(BaseModel):
    crop: str
    growth_stage: str
    soil_type: str
    current_moisture_pct: float
    optimal_target_pct: float
    critical_threshold_pct: float
    action: str
    badge_color: str
    title: str
    urgency: str
    recommended_volume_liters_m2: float
    drip_runtime_minutes: int
    explanation: str
    soil_advice: str
    weather_forecast_factor: str


# ── Agentic Advisor Schemas (Bonus G) ──
class AgenticCycleRequest(BaseModel):
    crop: str = Field("Tomato", description="Crop type")
    growth_stage: str = Field("Flowering", description="Growth stage")
    disease_name: Optional[str] = Field("Tomato Early Blight", description="Identified disease or 'healthy'")
    severity: Optional[str] = Field("High", description="Disease severity: Low, Medium, High, Critical")
    soil_moisture_pct: float = Field(32.0, ge=0, le=100, description="Current soil moisture %")
    soil_type: str = Field("Loamy", description="Soil texture")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AgenticNotification(BaseModel):
    id: str
    severity: str
    badge: str
    title: str
    message: str
    action_label: str
    action_code: str
    created_at: str


class AgenticDecisionLoopTrace(BaseModel):
    cycle_id: str
    timestamp: str
    perceive: List[Dict[str, Any]]
    reason: List[str]
    decide: List[Dict[str, Any]]
    notify: List[Dict[str, Any]]


class AgenticCycleResponse(BaseModel):
    status: str
    cycle_summary: str
    top_directive: str
    top_urgency: str
    notifications: List[AgenticNotification]
    decision_loop_trace: AgenticDecisionLoopTrace
    weather_context: Dict[str, Any]
    irrigation_context: Dict[str, Any]


# ── Crop Recommendation Schemas (Bonus A) ──
class CropRecommendationRequest(BaseModel):
    soil_type: str = Field("Loamy", description="Soil texture: Loamy, Clay, Sandy, Alluvial")
    ph: float = Field(6.5, ge=3.5, le=10.0, description="Soil pH level")
    temperature: Optional[float] = Field(26.0, description="Current or forecast temperature °C")
    rainfall_forecast_mm: Optional[float] = Field(45.0, description="Expected rainfall mm in coming weeks")
    season: str = Field("Kharif", description="Season: Kharif, Rabi, Zaid")
    previous_crop: Optional[str] = Field(None, description="Previous crop for rotation analysis")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RecommendedCropItem(BaseModel):
    crop: str
    suitability_pct: int
    duration: str
    water_requirement_mm: int
    rotation_benefit: str
    primary_rationale: str


class CropRecommendationResponse(BaseModel):
    status: str
    data_source: str
    input_parameters: Dict[str, Any]
    recommendations: List[RecommendedCropItem]


# ── Sustainability Schemas (Bonus D) ──
class SustainabilityEvaluateRequest(BaseModel):
    severity: str = Field("moderate", description="Disease severity: none, moderate, high, critical")
    irrigation_delayed_by_rain: bool = Field(False, description="Whether irrigation was delayed due to rain forecast")
    organic_chosen: bool = Field(True, description="Whether organic/biocontrol methods were selected")
    chemical_used: bool = Field(False, description="Whether synthetic chemical fungicides were applied")
    plot_acres: float = Field(1.0, ge=0.05, le=500.0, description="Plot size in acres")


class SustainabilityEvaluateResponse(BaseModel):
    sustainability_score: int
    grade: str
    grade_color: str
    metrics: Dict[str, Any]
    notes: Dict[str, str]
    improvement_suggestions: List[str]
    published_formula: str


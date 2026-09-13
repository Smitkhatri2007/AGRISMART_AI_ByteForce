"""
AgriSmart AI - Advisory & Autonomous Intelligence Router
Covers Bonus C (Weather), Bonus B (Irrigation), and Bonus G (Agentic Advisor)
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from app.services.weather_service import weather_service
from app.services.irrigation_service import irrigation_service
from app.services.agentic_service import agentic_service
from app.services.crop_recommendation_service import recommend_crops
from app.services.sustainability_service import evaluate_sustainability
from app.schemas.advisory import (
    WeatherIntelligenceResponse,
    IrrigationRequest,
    IrrigationResponse,
    AgenticCycleRequest,
    AgenticCycleResponse,
    CropRecommendationRequest,
    CropRecommendationResponse,
    SustainabilityEvaluateRequest,
    SustainabilityEvaluateResponse
)

router = APIRouter(prefix="/api/v1/advisory", tags=["Smart Advisory & Autonomous Agent"])


@router.get(
    "/weather",
    response_model=WeatherIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Weather-Based Agricultural Intelligence (Bonus C)",
    description=(
        "Retrieves live hyper-local weather and 7-day forecast from Open-Meteo. "
        "Evaluates chemical spraying windows, fungal disease outbreak risk, and rain-delay irrigation advice."
    )
)
async def get_weather_intelligence(
    lat: Optional[float] = Query(None, description="Latitude of the farm (e.g. 23.02)"),
    lon: Optional[float] = Query(None, description="Longitude of the farm (e.g. 72.57)")
):
    try:
        data = await weather_service.get_intelligence(lat=lat, lon=lon)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Weather Intelligence Error: {str(e)}"
        )


@router.post(
    "/irrigation",
    response_model=IrrigationResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Smart Irrigation Schedule (Bonus B)",
    description=(
        "Calculates crop water requirement using FAO-56 Management Allowed Depletion (MAD). "
        "Synthesizes farmer soil moisture input with upcoming 48h rain forecasts from Open-Meteo."
    )
)
async def calculate_irrigation(payload: IrrigationRequest):
    try:
        result = await irrigation_service.calculate_irrigation(
            crop=payload.crop,
            growth_stage=payload.growth_stage,
            soil_moisture_pct=payload.soil_moisture_pct,
            soil_type=payload.soil_type,
            lat=payload.latitude,
            lon=payload.longitude
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Irrigation Calculation Error: {str(e)}"
        )


@router.post(
    "/agentic/evaluate",
    response_model=AgenticCycleResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Autonomous Agentic Advisor Cycle (Bonus G)",
    description=(
        "Executes the 4-stage autonomous loop: Perceive -> Reason -> Decide -> Notify. "
        "Synthesizes disease detection, real-time weather, and soil conditions to dispatch proactive alerts."
    )
)
async def evaluate_agentic_cycle(payload: AgenticCycleRequest):
    try:
        cycle_result = await agentic_service.run_autonomous_cycle(
            crop=payload.crop,
            growth_stage=payload.growth_stage,
            disease_name=payload.disease_name,
            severity=payload.severity,
            soil_moisture_pct=payload.soil_moisture_pct,
            soil_type=payload.soil_type,
            lat=payload.latitude,
            lon=payload.longitude
        )
        return cycle_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agentic Cycle Execution Error: {str(e)}"
        )


@router.post(
    "/crop-recommendation",
    response_model=CropRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Recommend Crops based on Soil, pH & Weather (Bonus A)",
    description="Evaluates suitability across staple crops using ICAR/FAO agro-ecological criteria."
)
async def get_crop_recommendations(payload: CropRecommendationRequest):
    try:
        # If coordinates provided and weather temperature/rain not explicitly set, fetch live weather
        temp = payload.temperature or 26.0
        rain = payload.rainfall_forecast_mm or 45.0

        if payload.latitude and payload.longitude:
            try:
                w = await weather_service.get_intelligence(payload.latitude, payload.longitude)
                temp = w["current"]["temperature"]
                rain = w["irrigation_action"]["rain_48h_mm"] * 5  # extrapolate multi-week rainfall
            except Exception:
                pass

        result = recommend_crops(
            soil_type=payload.soil_type,
            ph=payload.ph,
            temperature=temp,
            rainfall_forecast_mm=rain,
            season=payload.season,
            previous_crop=payload.previous_crop
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crop Recommendation Error: {str(e)}"
        )


@router.post(
    "/sustainability/evaluate",
    response_model=SustainabilityEvaluateResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Farm Sustainability & Eco Score (Bonus D)",
    description="Computes indicative farm sustainability score with published formula and water saving metrics."
)
async def get_sustainability_score(payload: SustainabilityEvaluateRequest):
    try:
        result = evaluate_sustainability(
            severity=payload.severity,
            irrigation_delayed_by_rain=payload.irrigation_delayed_by_rain,
            organic_chosen=payload.organic_chosen,
            chemical_used=payload.chemical_used,
            plot_acres=payload.plot_acres
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sustainability Evaluation Error: {str(e)}"
        )


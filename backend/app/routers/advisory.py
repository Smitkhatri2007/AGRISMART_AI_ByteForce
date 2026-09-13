"""
AgriSmart AI - Advisory & Autonomous Intelligence Router
Covers Bonus C (Weather), Bonus B (Irrigation), and Bonus G (Agentic Advisor)
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from app.services.weather_service import weather_service
from app.services.irrigation_service import irrigation_service
from app.services.agentic_service import agentic_service
from app.schemas.advisory import (
    WeatherIntelligenceResponse,
    IrrigationRequest,
    IrrigationResponse,
    AgenticCycleRequest,
    AgenticCycleResponse
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

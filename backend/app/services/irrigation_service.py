"""
AgriSmart AI - Smart Irrigation Decision Engine
Bonus Module B (SIH 2026 Problem Statement 1)
Logic: FAO-56 Evapotranspiration & Management Allowed Depletion (MAD)
Cross-wired with live Open-Meteo weather precipitation forecast (Bonus C)
"""

import logging
from typing import Dict, Any, Optional
from app.services.weather_service import weather_service

logger = logging.getLogger("irrigation_service")

# Agronomic crop parameters: Optimal Moisture (%) and Critical Depletion (%) by stage
CROP_IRRIGATION_PROFILES = {
    "Tomato": {
        "Vegetative": {"optimal": 65, "critical": 45, "water_need_mm_day": 4.0},
        "Flowering": {"optimal": 75, "critical": 55, "water_need_mm_day": 6.5},  # Most sensitive
        "Fruiting": {"optimal": 70, "critical": 50, "water_need_mm_day": 5.5},
        "Maturity": {"optimal": 55, "critical": 35, "water_need_mm_day": 3.0},
    },
    "Potato": {
        "Vegetative": {"optimal": 65, "critical": 45, "water_need_mm_day": 3.5},
        "Flowering": {"optimal": 75, "critical": 55, "water_need_mm_day": 6.0},  # Tuber initiation
        "Fruiting": {"optimal": 70, "critical": 50, "water_need_mm_day": 5.0},
        "Maturity": {"optimal": 50, "critical": 30, "water_need_mm_day": 2.5},
    },
    "Corn": {
        "Vegetative": {"optimal": 60, "critical": 40, "water_need_mm_day": 4.5},
        "Flowering": {"optimal": 75, "critical": 55, "water_need_mm_day": 7.0},  # Tasseling/Silking
        "Fruiting": {"optimal": 65, "critical": 45, "water_need_mm_day": 5.0},
        "Maturity": {"optimal": 50, "critical": 35, "water_need_mm_day": 3.0},
    },
    "Bell Pepper": {
        "Vegetative": {"optimal": 65, "critical": 45, "water_need_mm_day": 3.8},
        "Flowering": {"optimal": 75, "critical": 55, "water_need_mm_day": 6.0},
        "Fruiting": {"optimal": 70, "critical": 50, "water_need_mm_day": 5.2},
        "Maturity": {"optimal": 55, "critical": 35, "water_need_mm_day": 3.0},
    },
    "Grape": {
        "Vegetative": {"optimal": 55, "critical": 35, "water_need_mm_day": 3.0},
        "Flowering": {"optimal": 65, "critical": 45, "water_need_mm_day": 4.5},
        "Fruiting": {"optimal": 60, "critical": 40, "water_need_mm_day": 4.0},
        "Maturity": {"optimal": 45, "critical": 25, "water_need_mm_day": 2.0},
    },
    "Apple": {
        "Vegetative": {"optimal": 60, "critical": 40, "water_need_mm_day": 3.5},
        "Flowering": {"optimal": 70, "critical": 50, "water_need_mm_day": 5.5},
        "Fruiting": {"optimal": 65, "critical": 45, "water_need_mm_day": 5.0},
        "Maturity": {"optimal": 50, "critical": 35, "water_need_mm_day": 3.0},
    }
}

DEFAULT_PROFILE = {
    "Vegetative": {"optimal": 60, "critical": 40, "water_need_mm_day": 4.0},
    "Flowering": {"optimal": 70, "critical": 50, "water_need_mm_day": 6.0},
    "Fruiting": {"optimal": 65, "critical": 45, "water_need_mm_day": 5.0},
    "Maturity": {"optimal": 50, "critical": 30, "water_need_mm_day": 3.0},
}

SOIL_FACTORS = {
    "Sandy": {"retention": 0.75, "drip_multiplier": 0.8, "advice": "Sandy soil drains rapidly. Short, frequent irrigation bursts recommended."},
    "Loamy": {"retention": 1.0, "drip_multiplier": 1.0, "advice": "Loamy soil has ideal balanced retention and aeration."},
    "Clay": {"retention": 1.25, "drip_multiplier": 1.2, "advice": "Clay soil holds moisture longer. Water slowly to prevent runoff and root asphyxiation."}
}


class IrrigationService:
    async def calculate_irrigation(
        self,
        crop: str,
        growth_stage: str,
        soil_moisture_pct: float,
        soil_type: str = "Loamy",
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict[str, Any]:
        # Clamp soil moisture to valid percentage
        try:
            soil_moisture_pct = max(0.0, min(100.0, float(soil_moisture_pct)))
        except (ValueError, TypeError):
            soil_moisture_pct = 50.0

        # Normalize crop name
        crop_clean = crop.replace("Pepper,_bell", "Bell Pepper").replace("Corn_(maize)", "Corn").strip()
        matched_crop = next((c for c in CROP_IRRIGATION_PROFILES.keys() if c.lower() in crop_clean.lower()), "Tomato")
        crop_config = CROP_IRRIGATION_PROFILES.get(matched_crop, DEFAULT_PROFILE)

        # Normalize stage
        stage_clean = growth_stage.capitalize() if growth_stage else "Flowering"
        if stage_clean not in crop_config:
            stage_clean = "Flowering"

        stage_data = crop_config[stage_clean]
        optimal_moisture = stage_data["optimal"]
        critical_moisture = stage_data["critical"]
        water_demand_mm = stage_data["water_need_mm_day"]

        soil_meta = SOIL_FACTORS.get(soil_type.capitalize(), SOIL_FACTORS["Loamy"])

        # Fetch live forecast from Bonus C weather service
        try:
            weather_data = await weather_service.get_intelligence(lat, lon)
            rain_action = weather_data.get("irrigation_action", {})
            rain_24h_mm = rain_action.get("rain_24h_mm", 0.0)
            prob_24h = rain_action.get("prob_24h_pct", 0)
            delay_from_weather = rain_action.get("delay_recommended", False)
            forecast_summary = f"{rain_24h_mm:.1f} mm rain expected in next 24h ({prob_24h}% chance)"
        except Exception as e:
            logger.warning(f"Failed to fetch weather for irrigation check: {e}")
            delay_from_weather = False
            rain_24h_mm = 0.0
            prob_24h = 0
            forecast_summary = "Forecast data unavailable; proceeding on soil metrics."

        # Severe drought check: near permanent wilting point (<= 60% of critical threshold)
        is_severe_drought = soil_moisture_pct <= (critical_moisture * 0.6)

        # ── Decision Tree ──
        # Scenario A: Rain is arriving soon
        if delay_from_weather or (rain_24h_mm >= 5.0 and prob_24h >= 40):
            if is_severe_drought:
                # Emergency light cycle to sustain root viability until precipitation arrives
                action = "EMERGENCY_SHORT_CYCLE"
                badge_color = "amber"
                title = "Emergency Short Cycle — Rain Approaching"
                urgency = "High"
                volume_liters_m2 = 2.5
                drip_minutes = int(round((volume_liters_m2 / 4.0) * 60))
                explanation = (
                    f"Severe soil depletion ({soil_moisture_pct:.0f}%) is near permanent wilting point for {matched_crop}. "
                    f"Although rain ({rain_24h_mm:.1f} mm, {prob_24h}% chance) is forecast, apply a brief emergency cycle "
                    f"of {volume_liters_m2} L/m² ({drip_minutes} mins drip) immediately to prevent irreversible plant collapse before precipitation begins."
                )
            else:
                action = "DELAY_IRRIGATION"
                badge_color = "amber"
                title = "Delay Irrigation — Rain Expected"
                urgency = "Low"
                volume_liters_m2 = 0.0
                drip_minutes = 0
                explanation = (
                    f"Natural precipitation ({rain_24h_mm:.1f} mm, {prob_24h}% chance) will replenish soil moisture. "
                    f"Irrigating now would risk oversaturating {matched_crop} root zone and causing root rot."
                )

        # Scenario B: Soil Moisture is below critical threshold
        elif soil_moisture_pct < critical_moisture:
            action = "IRRIGATE_NOW"
            badge_color = "red"
            title = "Irrigation Required Immediately"
            urgency = "High" if stage_clean in ["Flowering", "Fruiting"] or is_severe_drought else "Moderate"
            
            # Water deficit calculation in mm (1 mm = 1 Liter / m²)
            moisture_deficit_pct = max(0.0, optimal_moisture - soil_moisture_pct)
            # Factor soil retention and crop daily demand
            volume_liters_m2 = round((moisture_deficit_pct / 10.0) * water_demand_mm * 0.15 * soil_meta["retention"], 1)
            volume_liters_m2 = max(3.0, min(8.5, volume_liters_m2))
            
            # Standard drip line delivers ~4 Liters/m² per hour
            drip_minutes = int(round((volume_liters_m2 / 4.0) * 60))

            explanation = (
                f"Soil moisture ({soil_moisture_pct:.0f}%) is below the critical threshold ({critical_moisture}%) "
                f"for {matched_crop} during the {stage_clean} stage. Apply {volume_liters_m2} L/m² "
                f"({drip_minutes} minutes of drip irrigation) in the early morning to avoid yield stress."
            )

        # Scenario C: Moisture is adequate / optimal
        else:
            action = "OPTIMAL_MOISTURE"
            badge_color = "green"
            title = "Soil Moisture is Optimal"
            urgency = "None"
            volume_liters_m2 = 0.0
            drip_minutes = 0
            explanation = (
                f"Current moisture ({soil_moisture_pct:.0f}%) is within the healthy range ({critical_moisture}%–{optimal_moisture}%) "
                f"for {matched_crop} ({stage_clean} stage). No supplementary watering needed today."
            )

        return {
            "crop": matched_crop,
            "growth_stage": stage_clean,
            "soil_type": soil_type,
            "current_moisture_pct": soil_moisture_pct,
            "optimal_target_pct": optimal_moisture,
            "critical_threshold_pct": critical_moisture,
            "action": action,
            "badge_color": badge_color,
            "title": title,
            "urgency": urgency,
            "recommended_volume_liters_m2": volume_liters_m2,
            "drip_runtime_minutes": drip_minutes,
            "explanation": explanation,
            "soil_advice": soil_meta["advice"],
            "weather_forecast_factor": forecast_summary
        }


irrigation_service = IrrigationService()

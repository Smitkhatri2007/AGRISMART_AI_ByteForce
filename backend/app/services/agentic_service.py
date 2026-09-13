"""
AgriSmart AI - Autonomous Agentic Advisory Service
Bonus Module G (SIH 2026 Problem Statement 1)
Architecture: Autonomous 4-Stage Decision Loop:
  [1. PERCEIVE] -> [2. REASON] -> [3. DECIDE] -> [4. NOTIFY]
Synthesizes Leaf Disease Diagnosis + Live Weather Forecast + Soil Moisture
"""

import logging
from typing import Dict, Any, List, Optional
import datetime
from app.services.weather_service import weather_service
from app.services.irrigation_service import irrigation_service
from app.config import settings

logger = logging.getLogger("agentic_service")


class AgenticAdvisorService:
    async def run_autonomous_cycle(
        self,
        crop: str = "Tomato",
        growth_stage: str = "Flowering",
        disease_name: Optional[str] = "Tomato Early Blight",
        severity: Optional[str] = "High",
        soil_moisture_pct: float = 32.0,
        soil_type: str = "Loamy",
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes an end-to-end autonomous agentic reasoning cycle.
        """
        trace = {
            "cycle_id": f"agent_cycle_{int(datetime.datetime.now().timestamp())}",
            "timestamp": datetime.datetime.now().isoformat(),
            "perceive": [],
            "reason": [],
            "decide": [],
            "notify": []
        }

        # ─────────────────────────────────────────────────────────────
        # STAGE 1: PERCEIVE (Ingest Multimodal & Environmental Telemetry)
        # ─────────────────────────────────────────────────────────────
        # 1.1 Ingest Disease Telemetry
        is_diseased = bool(disease_name and "healthy" not in disease_name.lower())
        trace["perceive"].append({
            "source": "Computer Vision Core Model",
            "observation": f"Crop: {crop} ({growth_stage} stage). Status: {disease_name if is_diseased else 'Healthy'}.",
            "severity": severity if is_diseased else "None"
        })

        # 1.2 Ingest Live Weather Telemetry
        weather_intel = await weather_service.get_intelligence(lat, lon)
        current_w = weather_intel.get("current", {})
        rain_action = weather_intel.get("irrigation_action", {})
        spray_info = weather_intel.get("spray_window", {})
        disease_risk = weather_intel.get("disease_risk", {})

        trace["perceive"].append({
            "source": "Open-Meteo Weather Model",
            "observation": f"Temp: {current_w.get('temperature')}°C, Humidity: {current_w.get('humidity')}%, Wind: {current_w.get('wind_speed')} km/h. "
                           f"Rain 24h: {rain_action.get('rain_24h_mm', 0)} mm ({rain_action.get('prob_24h_pct', 0)}% prob)."
        })

        # 1.3 Ingest Soil Telemetry
        irrigation_calc = await irrigation_service.calculate_irrigation(
            crop=crop,
            growth_stage=growth_stage,
            soil_moisture_pct=soil_moisture_pct,
            soil_type=soil_type,
            lat=lat,
            lon=lon
        )
        trace["perceive"].append({
            "source": "Soil Moisture Subsystem",
            "observation": f"Soil Moisture: {soil_moisture_pct:.0f}% ({soil_type} soil). Irrigation demand: {irrigation_calc.get('action')}."
        })

        # ─────────────────────────────────────────────────────────────
        # STAGE 2: REASON (Cross-Domain Conflict & Risk Synthesis)
        # ─────────────────────────────────────────────────────────────
        reasons = []
        priorities = []

        # Conflict 1: Disease Spray vs Weather Conditions
        if is_diseased:
            if current_w.get("wind_speed", 0) >= 16.0 or rain_action.get("prob_24h_pct", 0) >= 40:
                reasons.append(
                    f"CONFLICT DETECTED: {disease_name} requires fungicide/pesticide treatment, BUT weather conditions are unfavorable "
                    f"(Wind: {current_w.get('wind_speed')} km/h, Rain chance: {rain_action.get('prob_24h_pct')}%, Spray Status: {spray_info.get('status')}). "
                    f"Applying chemicals now will cause chemical drift and pesticide wash-off into groundwater."
                )
                priorities.append("HIGH_WEATHER_SPRAY_CONFLICT")
            else:
                reasons.append(
                    f"TREATMENT WINDOW OPEN: {disease_name} requires treatment and current weather allows safe application "
                    f"(Wind < 15 km/h, no imminent rain)."
                )

        # Conflict 2: Irrigation vs Rainfall Forecast
        if rain_action.get("delay_recommended") or (rain_action.get("rain_24h_mm", 0) >= 4.0):
            reasons.append(
                f"RESOURCE OPTIMIZATION: Soil moisture is {soil_moisture_pct:.0f}%, but {rain_action.get('rain_24h_mm'):.1f} mm rain is "
                f"approaching within 24h. Postponing irrigation conserves water, electricity, and protects root aeration."
            )
            priorities.append("IRRIGATION_POSTPONEMENT")
        elif soil_moisture_pct < irrigation_calc.get("critical_threshold_pct", 45):
            reasons.append(
                f"DROUGHT STRESS RISK: Soil moisture ({soil_moisture_pct:.0f}%) is below {growth_stage} threshold "
                f"({irrigation_calc.get('critical_threshold_pct')}%) with no rain expected. Immediate supplementary irrigation required."
            )
            priorities.append("URGENT_IRRIGATION_NEEDED")

        # Conflict 3: Fungal Spore Acceleration Risk
        if disease_risk.get("level") in ["HIGH", "CRITICAL"]:
            reasons.append(
                f"EPIDEMIC THREAT: Regional atmospheric humidity ({current_w.get('humidity')}%) and temperature ({current_w.get('temperature')}°C) "
                f"are at optimal fungal germination levels ({disease_risk.get('favorable_humidity_hours')} hours of leaf wetness). "
                f"Pathogen reproduction will accelerate across healthy neighboring crops."
            )
            priorities.append("FUNGAL_EPIDEMIC_RISK")

        trace["reason"] = reasons

        # ─────────────────────────────────────────────────────────────
        # STAGE 3: DECIDE (Formulate Autonomous Tactical Strategy)
        # ─────────────────────────────────────────────────────────────
        decisions = []

        if "HIGH_WEATHER_SPRAY_CONFLICT" in priorities:
            decisions.append({
                "action": "SUSPEND_SPRAYING",
                "priority": "Critical",
                "directive": "Hold Chemical Spraying Until Tomorrow Morning",
                "rationale": "High wind/rain will cause 80%+ chemical waste and environmental contamination. Spray between 06:00 AM – 09:00 AM once wind stabilizes.",
                "action_type": "chemical_timing"
            })

        if "IRRIGATION_POSTPONEMENT" in priorities:
            decisions.append({
                "action": "PAUSE_IRRIGATION",
                "priority": "High",
                "directive": "Hold Drip Irrigation for Next 24 Hours",
                "rationale": f"Natural rainfall (~{rain_action.get('rain_24h_mm', 0):.1f} mm) will recharge the root zone. Prevents waterlogging and root rot in {crop}.",
                "action_type": "water_conservation"
            })
        elif "URGENT_IRRIGATION_NEEDED" in priorities:
            decisions.append({
                "action": "SCHEDULE_IRRIGATION",
                "priority": "High",
                "directive": f"Apply {irrigation_calc.get('recommended_volume_liters_m2')} L/m² Drip Irrigation",
                "rationale": f"{crop} is in critical {growth_stage} stage and experiencing moisture depletion.",
                "action_type": "irrigation_dispatch"
            })

        if "FUNGAL_EPIDEMIC_RISK" in priorities:
            decisions.append({
                "action": "CANOPY_VENTILATION",
                "priority": "Medium",
                "directive": "Improve Air Circulation & Prune Affected Lower Foliage",
                "rationale": "Dense wet canopies promote rapid blight sporulation. Prune lowest yellowing leaves to allow airflow.",
                "action_type": "cultural_sanitation"
            })

        if not decisions:
            decisions.append({
                "action": "CONTINUE_MONITORING",
                "priority": "Normal",
                "directive": "Farm Ecosystem in Healthy Equilibrium",
                "rationale": "Soil moisture is balanced, weather is calm, and disease risks remain within safe limits.",
                "action_type": "routine"
            })

        trace["decide"] = decisions

        # ─────────────────────────────────────────────────────────────
        # STAGE 4: NOTIFY (Emit Actionable Proactive Farmer Notifications)
        # ─────────────────────────────────────────────────────────────
        notifications = []
        for idx, dec in enumerate(decisions):
            severity_tag = "urgent" if dec["priority"] == "Critical" else ("warning" if dec["priority"] == "High" else "info")
            notifications.append({
                "id": f"notif_{idx + 1}",
                "severity": severity_tag,
                "badge": dec["priority"].upper(),
                "title": dec["directive"],
                "message": dec["rationale"],
                "action_label": "Apply Recommendation",
                "action_code": dec["action"],
                "created_at": datetime.datetime.now().strftime("%I:%M %p")
            })

        trace["notify"] = notifications

        return {
            "status": "success",
            "cycle_summary": f"Agentic Advisor evaluated {len(trace['perceive'])} observation domains, identified {len(reasons)} core correlations, and dispatched {len(notifications)} proactive directives.",
            "top_directive": decisions[0]["directive"] if decisions else "All parameters optimal",
            "top_urgency": decisions[0]["priority"] if decisions else "Normal",
            "notifications": notifications,
            "decision_loop_trace": trace,
            "weather_context": {
                "temp": current_w.get("temperature"),
                "humidity": current_w.get("humidity"),
                "wind": current_w.get("wind_speed"),
                "rain_24h_mm": rain_action.get("rain_24h_mm", 0.0)
            },
            "irrigation_context": {
                "action": irrigation_calc.get("action"),
                "soil_moisture": soil_moisture_pct,
                "recommended_liters": irrigation_calc.get("recommended_volume_liters_m2")
            }
        }


agentic_service = AgenticAdvisorService()

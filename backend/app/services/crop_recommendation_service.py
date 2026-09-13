# ==========================================================================
# AgriSmart AI - Crop Recommendation Engine (Bonus Module A)
# Grounded in ICAR (Indian Council of Agricultural Research) & FAO Guidelines
# ==========================================================================

from typing import List, Dict, Any, Optional

CROP_DATABASE = [
    {
        "crop": "Maize (Corn)",
        "optimal_soil": ["loamy", "clay", "alluvial"],
        "min_ph": 5.8, "max_ph": 7.2,
        "min_temp": 18, "max_temp": 35,
        "min_rain": 40, "max_rain": 120,
        "season": ["Kharif", "Rabi"],
        "water_req_mm": 500,
        "duration_days": "90-110",
        "beneficial_after": ["Tomato", "Potato", "Chickpea", "Legumes"],
        "rotation_advantage": "Breaks solanaceous fungal blight cycles and utilizes residual nitrogen."
    },
    {
        "crop": "Chickpea (Gram)",
        "optimal_soil": ["loamy", "clay", "sandy"],
        "min_ph": 6.0, "max_ph": 8.0,
        "min_temp": 15, "max_temp": 30,
        "min_rain": 20, "max_rain": 70,
        "season": ["Rabi"],
        "water_req_mm": 350,
        "duration_days": "100-120",
        "beneficial_after": ["Corn", "Rice", "Wheat", "Tomato"],
        "rotation_advantage": "Biological nitrogen fixation (Rhizobium) enriches soil fertility for subsequent heavy feeders."
    },
    {
        "crop": "Mustard",
        "optimal_soil": ["loamy", "alluvial", "sandy"],
        "min_ph": 6.0, "max_ph": 7.5,
        "min_temp": 10, "max_temp": 28,
        "min_rain": 15, "max_rain": 60,
        "season": ["Rabi"],
        "water_req_mm": 250,
        "duration_days": "105-130",
        "beneficial_after": ["Cotton", "Corn", "Rice"],
        "rotation_advantage": "Deep taproot system opens subsoil compaction with low moisture demand."
    },
    {
        "crop": "Tomato",
        "optimal_soil": ["loamy", "sandy"],
        "min_ph": 6.0, "max_ph": 7.0,
        "min_temp": 18, "max_temp": 32,
        "min_rain": 30, "max_rain": 90,
        "season": ["Kharif", "Rabi", "Zaid"],
        "water_req_mm": 600,
        "duration_days": "90-120",
        "beneficial_after": ["Legumes", "Corn", "Wheat"],
        "rotation_advantage": "High economic return when rotated away from solanaceous nightshade families."
    },
    {
        "crop": "Groundnut (Peanut)",
        "optimal_soil": ["sandy", "loamy"],
        "min_ph": 5.5, "max_ph": 7.0,
        "min_temp": 22, "max_temp": 34,
        "min_rain": 40, "max_rain": 100,
        "season": ["Kharif", "Zaid"],
        "water_req_mm": 450,
        "duration_days": "100-125",
        "beneficial_after": ["Wheat", "Corn"],
        "rotation_advantage": "Excellent cover crop that minimizes soil erosion while fixing atmospheric nitrogen."
    },
    {
        "crop": "Wheat",
        "optimal_soil": ["loamy", "clay"],
        "min_ph": 6.0, "max_ph": 7.5,
        "min_temp": 12, "max_temp": 26,
        "min_rain": 25, "max_rain": 80,
        "season": ["Rabi"],
        "water_req_mm": 450,
        "duration_days": "120-140",
        "beneficial_after": ["Soybean", "Rice", "Groundnut"],
        "rotation_advantage": "Reliable winter staple utilizing residual legume nitrogen."
    },
    {
        "crop": "Bell Pepper (Capsicum)",
        "optimal_soil": ["loamy"],
        "min_ph": 6.0, "max_ph": 6.8,
        "min_temp": 18, "max_temp": 30,
        "min_rain": 40, "max_rain": 90,
        "season": ["Kharif", "Rabi"],
        "water_req_mm": 550,
        "duration_days": "90-110",
        "beneficial_after": ["Legumes", "Corn"],
        "rotation_advantage": "High value horticultural crop with drip irrigation precision."
    },
    {
        "crop": "Soybean",
        "optimal_soil": ["loamy", "clay"],
        "min_ph": 6.0, "max_ph": 7.5,
        "min_temp": 20, "max_temp": 32,
        "min_rain": 50, "max_rain": 120,
        "season": ["Kharif"],
        "water_req_mm": 500,
        "duration_days": "90-115",
        "beneficial_after": ["Wheat", "Mustard"],
        "rotation_advantage": "Improves organic matter and replenishes soil microbial biodiversity."
    }
]

def recommend_crops(
    soil_type: str,
    ph: float,
    temperature: float,
    rainfall_forecast_mm: float,
    season: str = "Kharif",
    previous_crop: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates crop suitability against agronomic criteria and rotation history.
    """
    soil_clean = soil_type.lower().strip()
    season_clean = season.strip()
    prev_clean = (previous_crop or "").lower().strip()

    scored_crops = []

    for item in CROP_DATABASE:
        score = 0
        reasons = []

        # 1. Soil Match (Weight 25)
        if any(s in soil_clean for s in item["optimal_soil"]):
            score += 25
            reasons.append(f"Soil texture '{soil_type}' matches optimal rooting conditions.")
        else:
            score += 10
            reasons.append(f"Moderate adaptation to '{soil_type}' soil.")

        # 2. pH Match (Weight 20)
        if item["min_ph"] <= ph <= item["max_ph"]:
            score += 20
            reasons.append(f"Soil pH {ph} is within optimum range ({item['min_ph']} - {item['max_ph']}).")
        elif abs(ph - item["min_ph"]) <= 0.6 or abs(ph - item["max_ph"]) <= 0.6:
            score += 12
            reasons.append(f"Soil pH {ph} is tolerable with slight conditioning.")
        else:
            score += 5

        # 3. Temperature Match (Weight 20)
        if item["min_temp"] <= temperature <= item["max_temp"]:
            score += 20
            reasons.append(f"Current temperature {temperature:.1f}°C is in the growth comfort zone.")
        else:
            score += 8

        # 4. Rainfall / Moisture Match (Weight 15)
        if item["min_rain"] <= rainfall_forecast_mm <= item["max_rain"]:
            score += 15
            reasons.append(f"Forecast rain {rainfall_forecast_mm:.1f}mm satisfies base germination water demand.")
        else:
            score += 8
            reasons.append("Supplemental drip irrigation recommended for target yield.")

        # 5. Season Match (Weight 10)
        if season_clean in item["season"]:
            score += 10
        else:
            score += 2

        # 6. Crop Rotation Bonus (Weight 10)
        if prev_clean:
            if any(p.lower() in prev_clean for p in item["beneficial_after"]):
                score += 10
                reasons.append(f"Rotation advantage: {item['rotation_advantage']}")
            elif prev_clean in item["crop"].lower():
                score -= 15
                reasons.append("Warning: Monoculture risk. Avoid planting same family consecutively.")

        suitability = min(100, max(20, score))
        scored_crops.append({
            "crop": item["crop"],
            "suitability_pct": suitability,
            "duration": item["duration_days"],
            "water_requirement_mm": item["water_req_mm"],
            "rotation_benefit": item["rotation_advantage"],
            "primary_rationale": " ".join(reasons[:2])
        })

    # Sort by suitability descending
    scored_crops.sort(key=lambda x: x["suitability_pct"], reverse=True)
    top_recommendations = scored_crops[:3]

    return {
        "status": "success",
        "data_source": "ICAR & FAO Agro-Ecological Suitability Standards",
        "input_parameters": {
            "soil_type": soil_type,
            "ph": ph,
            "temperature_c": temperature,
            "rainfall_forecast_mm": rainfall_forecast_mm,
            "season": season,
            "previous_crop": previous_crop or "None specified"
        },
        "recommendations": top_recommendations
    }

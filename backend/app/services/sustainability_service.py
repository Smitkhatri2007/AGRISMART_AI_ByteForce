# ==========================================================================
# AgriSmart AI - Sustainability & Resource Conservation Engine (Bonus Module D)
# Transparent reproducible scoring for water efficiency, resource use & crop health
# ==========================================================================

from typing import Dict, Any, List, Optional

PUBLISHED_FORMULA = """
Sustainability Score (S) = (0.35 * H) + (0.35 * W) + (0.30 * O) - P_chem
Where:
- H: Crop Health Index (0-100) based on disease severity.
- W: Water Efficiency Index (0-100) factoring FAO-56 irrigation delay during rain forecasts.
- O: Organic Stewardship Index (0-100) evaluating adoption of bio-pesticides and organic IPM.
- P_chem: Chemical Runoff Penalty (0-20) deducted for untargeted high-toxicity chemical application.
Grade: A+ (>=90), A (80-89), B (65-79), C (50-64), Needs Remediation (<50).
"""

def evaluate_sustainability(
    severity: str,
    irrigation_delayed_by_rain: bool,
    organic_chosen: bool,
    chemical_used: bool,
    plot_acres: float = 1.0
) -> Dict[str, Any]:
    """
    Computes indicative farm sustainability score, water saved in liters,
    and chemical reduction percentage with actionable improvements.
    """
    sev = severity.lower()

    # 1. Health Index (H: 0 - 100)
    if sev in ["none", "healthy"]:
        h = 100
        health_note = "Crop foliage is clean and photosynthetically optimal."
    elif sev == "moderate":
        h = 80
        health_note = "Early localized symptoms detected; manageable without systemic crop loss."
    elif sev == "high":
        h = 55
        health_note = "Widespread infection requires urgent biocontrol containment."
    else:  # critical
        h = 30
        health_note = "Severe canopy necrosis; immediate IPM intervention required."

    # 2. Water Efficiency Index (W: 0 - 100)
    # Average drip irrigation uses approx 25,000 - 30,000 Litres per acre per watering cycle.
    # Delaying irrigation during upcoming rainfall saves significant ground water.
    water_saved_liters = 0.0
    if irrigation_delayed_by_rain:
        w = 95
        water_saved_liters = round(plot_acres * 24500.0, 1)  # ~24,500 L saved per acre cycle
        water_note = f"Smart Rain Delay activated: Conserved estimated {water_saved_liters:,.0f} L of groundwater."
    else:
        w = 75
        water_note = "Standard FAO-56 precision drip irrigation schedule maintained."

    # 3. Organic Stewardship Index (O: 0 - 100)
    if organic_chosen:
        o = 100
        org_note = "Bio-fungicides / cold-pressed neem oils preserve beneficial soil microbes and pollinators."
    else:
        o = 50
        org_note = "No biological agents declared in current management plan."

    # 4. Chemical Penalty (P_chem: 0 - 20)
    if chemical_used:
        p_chem = 15.0
        chem_runoff_reduction_pct = 35.0  # partial containment
        chem_note = "Synthetic chemical spray applied: Runoff mitigation required."
    else:
        p_chem = 0.0
        chem_runoff_reduction_pct = 100.0  # zero synthetic chemical runoff
        chem_note = "Zero synthetic fungicides applied: 100% reduction in chemical runoff."

    # Final Score
    raw_score = (0.35 * h) + (0.35 * w) + (0.30 * o) - p_chem
    final_score = int(round(max(0, min(100, raw_score))))

    # Assign Grade
    if final_score >= 90:
        grade = "A+ (Exemplary Sustainable)"
        grade_color = "#166534"
    elif final_score >= 80:
        grade = "A (Eco-Conscious)"
        grade_color = "#2e7d32"
    elif final_score >= 65:
        grade = "B (Moderate Impact)"
        grade_color = "#f59e0b"
    elif final_score >= 50:
        grade = "C (Transitioning)"
        grade_color = "#ea580c"
    else:
        grade = "D (Remediation Needed)"
        grade_color = "#dc2626"

    # Actionable Improvement Suggestions
    suggestions: List[str] = []
    if chemical_used:
        suggestions.append("Replace synthetic chemical sprays with Trichoderma harzianum or Bacillus subtilis bio-agents to gain +15 points.")
    if not irrigation_delayed_by_rain:
        suggestions.append("Check the 48-hour rainfall forecast before running drip lines to prevent fertilizer leaching and gain +10 points.")
    if not organic_chosen:
        suggestions.append("Incorporate 5ml/L cold-pressed Neem Oil as a preventative foliar coating to elevate your organic score.")
    if sev in ["high", "critical"]:
        suggestions.append("Prune and deep-bury infected lower leaves immediately to prevent spore dispersal.")

    return {
        "sustainability_score": final_score,
        "grade": grade,
        "grade_color": grade_color,
        "metrics": {
            "health_index": h,
            "water_efficiency_index": w,
            "organic_stewardship_index": o,
            "chemical_penalty": p_chem,
            "water_saved_liters": water_saved_liters,
            "chemical_runoff_reduction_pct": chem_runoff_reduction_pct
        },
        "notes": {
            "health": health_note,
            "water": water_note,
            "organic": org_note,
            "chemical": chem_note
        },
        "improvement_suggestions": suggestions,
        "published_formula": PUBLISHED_FORMULA.strip()
    }

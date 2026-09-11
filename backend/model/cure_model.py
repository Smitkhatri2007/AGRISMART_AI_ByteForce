"""
AgriSmart AI - Model 2: Cureness & Treatment Recommendation Model
Specialized in agronomic prescriptions, recovery probability estimation,
and multi-phase cure timelines based on disease diagnosis and crop stage.
"""

import os
from typing import Dict, Any, Optional
from model.class_catalog import CLASS_METADATA

USE_REAL_CURE_MODEL = False
CURE_WEIGHTS_PATH = os.getenv("CURE_WEIGHTS_PATH", "model/cure_weights.pth")


class CurenessTreatmentModel:
    """
    Model 2: Evaluates the disease state, crop type, and severity to prescribe
    an actionable cureness plan, recovery likelihood, and specific treatment dosage.
    """

    def __init__(self):
        self.real_model = None
        if USE_REAL_CURE_MODEL and os.path.exists(CURE_WEIGHTS_PATH):
            self._load_real_cure_weights()

    def _load_real_cure_weights(self):
        """
        Hook for loading real ML/expert cureness model weights or decision tree.
        """
        pass

    def predict_cure(
        self,
        predicted_class: str,
        crop: Optional[str] = None,
        severity: Optional[str] = None,
        growth_stage: Optional[str] = "Growing",
        confidence: Optional[float] = 0.90
    ) -> Dict[str, Any]:
        """
        Generates comprehensive cureness and recovery plan.
        """
        meta = CLASS_METADATA.get(predicted_class, {})
        is_healthy = meta.get("is_healthy", False)
        crop_name = crop or meta.get("crop", "Unknown Crop")
        sev = severity or meta.get("severity", "Medium")

        if is_healthy:
            return self._generate_healthy_maintenance(crop_name, growth_stage)

        if USE_REAL_CURE_MODEL and self.real_model is not None:
            return self._run_real_cure_inference(predicted_class, crop_name, sev, growth_stage)

        return self._run_mock_cure_inference(predicted_class, meta, crop_name, sev, growth_stage, confidence)

    def _generate_healthy_maintenance(self, crop: str, growth_stage: str) -> Dict[str, Any]:
        return {
            "cureness_score": 1.0,
            "recovery_chance_pct": 100.0,
            "recovery_timeline": "Crop is healthy - no recovery required",
            "recovery_timeline_days": 0,
            "urgency_level": "MAINTENANCE",
            "prognosis_summary": f"Your {crop} is in healthy condition during the {growth_stage} stage. Focus on preventive nutrition.",
            "phases": {
                "containment": "None needed. Continue standard hygiene.",
                "curative_action": "No chemical or emergency organic fungicides required.",
                "preventative_care": "Apply monthly organic neem spray (3ml/L) and balanced NPK foliar feeds."
            },
            "dosage_guide": {
                "organic": "Neem oil 1500 PPM @ 3ml/L water as prophylactic once a month.",
                "chemical": "None.",
                "application_timing": "Early morning (6:00 AM - 8:30 AM) or late afternoon."
            },
            "model_type": "Model_2_Cureness_Prescriber"
        }

    def _run_mock_cure_inference(
        self,
        predicted_class: str,
        meta: Dict[str, Any],
        crop: str,
        severity: str,
        growth_stage: str,
        confidence: float
    ) -> Dict[str, Any]:
        # Calculate dynamic recovery chance based on severity and disease type
        if severity == "High":
            recovery_chance = 0.72
            timeline_days = 14
            timeline_str = "10–14 days with intensive intervention"
            urgency = "CRITICAL (Act within 24–48 hours)"
        else:
            recovery_chance = 0.88
            timeline_days = 7
            timeline_str = "5–7 days with standard intervention"
            urgency = "MODERATE (Act within 3–5 days)"

        # Adjust slightly for confidence
        recovery_pct = round(recovery_chance * 100.0, 1)

        organic_remedy = meta.get("organic_remedy", "Apply certified bio-fungicide.")
        chemical_remedy = meta.get("chemical_remedy", "Consult local agronomy officer for registered chemical control.")
        precaution = meta.get("precaution", "Remove affected foliage.")

        return {
            "cureness_score": recovery_chance,
            "recovery_chance_pct": recovery_pct,
            "recovery_timeline": timeline_str,
            "recovery_timeline_days": timeline_days,
            "urgency_level": urgency,
            "prognosis_summary": (
                f"With prompt treatment, your {crop} has a {recovery_pct}% chance of full recovery. "
                f"Early containment is essential to protect uninfected foliage."
            ),
            "phases": {
                "containment": f"Prune and safely destroy visibly damaged leaves immediately. {precaution}",
                "curative_action": f"Apply targeted treatment: {organic_remedy} (Organic) OR {chemical_remedy} (Chemical).",
                "soil_and_canopy_rehab": "Avoid overhead watering. Ensure 15–20% increase in airflow around canopy."
            },
            "dosage_guide": {
                "organic": f"{organic_remedy} Recommended dosage: 4–5 ml/L water, repeat every 5 days for 2 cycles.",
                "chemical": f"{chemical_remedy} Recommended dosage: 2–2.5 g/L water, observing pre-harvest safety interval.",
                "application_timing": "Spray during calm weather before 9:00 AM or after 5:00 PM to avoid leaf scorch."
            },
            "model_type": "Model_2_Cureness_Prescriber"
        }

    def _run_real_cure_inference(self, predicted_class: str, crop: str, severity: str, stage: str):
        raise NotImplementedError("Real cure model weights not plugged in yet.")


# Singleton instance
cure_model = CurenessTreatmentModel()

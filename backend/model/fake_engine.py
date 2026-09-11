"""
AgriSmart AI - Unified Dual Model Inference Orchestrator
Coordinates:
- Model 1: DiseaseDetectionModel (Leaf Image -> Disease Class & Severity)
- Model 2: CurenessTreatmentModel (Disease & Stage -> Recovery Chance & Treatment Regimen)
Ref: SIH 2026 Problem Statement 1
"""

from typing import Dict, Any, Optional
from model.disease_model import disease_model
from model.cure_model import cure_model


class DualModelOrchestrator:
    """
    Coordinates Model 1 (Disease Detection) and Model 2 (Cureness & Treatment).
    """

    def __init__(self):
        self.disease_model = disease_model
        self.cure_model = cure_model

    def predict(self, image_path: str) -> str:
        """
        Mandatory submission interface contract:
        predict(image_path) -> class_label
        Delegates strictly to Model 1.
        """
        return self.disease_model.predict_class(image_path)

    def predict_detailed(self, image_path: str, growth_stage: Optional[str] = "Growing") -> Dict[str, Any]:
        """
        Chains Model 1 (Disease Detection) -> Model 2 (Cureness Treatment):
        1. Model 1 identifies disease, crop, confidence, and severity from image.
        2. Model 2 prescribes the cureness recovery score, multi-phase action, and dosages.
        """
        # Step 1: Execute Model 1
        detection = self.disease_model.predict_detailed(image_path)

        # Step 2: Execute Model 2 using outputs of Model 1
        cure_plan = self.cure_model.predict_cure(
            predicted_class=detection["predicted_class"],
            crop=detection["crop"],
            severity=detection["severity"],
            growth_stage=growth_stage,
            confidence=detection["confidence"]
        )

        # Merge results into unified diagnostic package
        return {
            "predicted_class": detection["predicted_class"],
            "confidence": detection["confidence"],
            "is_healthy": detection["is_healthy"],
            "crop": detection["crop"],
            "disease_name": detection["disease_name"],
            "severity": detection["severity"],
            "top_k": detection["top_k"],
            "image_dimensions": detection["image_dimensions"],
            "cureness_plan": cure_plan,
            # Flattened convenience fields for backward compatibility
            "precaution": cure_plan["phases"]["containment"],
            "organic_remedy": cure_plan["dosage_guide"]["organic"],
            "chemical_remedy": cure_plan["dosage_guide"]["chemical"],
            "recovery_chance_pct": cure_plan["recovery_chance_pct"],
            "recovery_timeline": cure_plan["recovery_timeline"],
            "urgency_level": cure_plan["urgency_level"],
            "architecture": "Dual_AI_Engine (Model 1: Disease + Model 2: Cureness)"
        }

    def predict_cure_only(
        self,
        predicted_class: str,
        crop: Optional[str] = None,
        severity: Optional[str] = None,
        growth_stage: Optional[str] = "Growing"
    ) -> Dict[str, Any]:
        """Direct call to Model 2 when disease is already known."""
        return self.cure_model.predict_cure(
            predicted_class=predicted_class,
            crop=crop,
            severity=severity,
            growth_stage=growth_stage
        )


# Global singleton instance
default_engine = DualModelOrchestrator()

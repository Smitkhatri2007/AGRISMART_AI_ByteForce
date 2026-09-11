"""
AgriSmart AI - Model Inference Orchestrator
Uses the single Computer Vision model for crop disease classification,
with Gemini Pro generating contextual descriptions and on-demand cureness plans.
Ref: SIH 2026 Problem Statement 1
"""

from typing import Dict, Any, Optional
from model.disease_model import disease_model


class DiseaseModelOrchestrator:
    """
    Orchestrates the single Disease Detection model.
    """

    def __init__(self):
        self.disease_model = disease_model

    def predict(self, image_path: str) -> str:
        """
        Mandatory submission interface contract:
        predict(image_path) -> class_label
        Delegates directly to the single disease detection model.
        """
        return self.disease_model.predict_class(image_path)

    def predict_detailed(self, image_path: str) -> Dict[str, Any]:
        """
        Runs the CV model on the leaf image and returns full detection metadata.
        """
        return self.disease_model.predict_detailed(image_path)


# Global singleton instance
default_engine = DiseaseModelOrchestrator()

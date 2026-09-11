"""
AgriSmart AI - Model Package
Exports:
- predict: Mandatory submission function (predict(image_path) -> class_label)
- disease_model: The single Computer Vision Disease Detector
- default_engine: Model Orchestrator
"""
from model.predict import predict
from model.disease_model import disease_model
from model.fake_engine import default_engine

__all__ = ["predict", "disease_model", "default_engine"]

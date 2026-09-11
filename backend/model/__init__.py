"""
AgriSmart AI - Model Package
Exports:
- predict: Mandatory submission function
- disease_model: Model 1 (Computer Vision Disease Detector)
- cure_model: Model 2 (Agronomic Cureness & Treatment Prescriber)
- default_engine: Dual-Model Orchestrator
"""
from model.predict import predict
from model.disease_model import disease_model
from model.cure_model import cure_model
from model.fake_engine import default_engine

__all__ = ["predict", "disease_model", "cure_model", "default_engine"]

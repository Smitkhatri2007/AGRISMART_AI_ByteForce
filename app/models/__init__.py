"""
SQLAlchemy ORM Models
"""
from app.models.farm import Farmer, Farm, Crop
from app.models.diagnosis import DiseasePrediction

__all__ = ["Farmer", "Farm", "Crop", "DiseasePrediction"]

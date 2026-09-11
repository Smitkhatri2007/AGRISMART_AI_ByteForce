"""
AgriSmart AI - Disease Diagnosis & Gemini Pro Advisory Audit Entity
Logs CV disease detections, Gemini Pro descriptions, and generated cure plans.
"""

import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    image_filename = Column(String(255), nullable=False)
    
    # CV Model Outputs
    predicted_class = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    is_healthy = Column(Boolean, default=False)
    severity = Column(String(20), default="Medium")
    
    # Gemini Pro Generative Outputs
    disease_description = Column(Text, nullable=True)
    cure_prompt = Column(Text, nullable=True)
    recovery_chance_pct = Column(Float, nullable=True)
    recovery_timeline = Column(String(100), nullable=True)
    organic_treatment = Column(Text, nullable=True)
    chemical_treatment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    farm = relationship("Farm", back_populates="diagnoses")

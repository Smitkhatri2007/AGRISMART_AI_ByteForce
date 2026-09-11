"""
AgriSmart AI - Disease Prediction & Cureness Audit Entity
Logs Model 1 disease classifications and Model 2 cureness prescriptions.
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
    
    # Model 1: Disease Detection outputs
    predicted_class = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    is_healthy = Column(Boolean, default=False)
    severity = Column(String(20), default="Medium")
    
    # Model 2: Cureness & Treatment outputs
    recovery_chance_pct = Column(Float, nullable=True)
    recovery_timeline = Column(String(100), nullable=True)
    urgency_level = Column(String(50), default="MODERATE")
    precaution = Column(Text, nullable=True)
    organic_remedy = Column(Text, nullable=True)
    chemical_remedy = Column(Text, nullable=True)
    prognosis_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    farm = relationship("Farm", back_populates="diagnoses")

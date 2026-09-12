"""
AgriSmart AI - Farmer, Farm, and Crop ORM Entities
"""

import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    preferred_language = Column(String(10), default="en")  # 'en', 'hi', 'mr'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farms = relationship("Farm", back_populates="farmer", cascade="all, delete-orphan")


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    name = Column(String(100), default="Primary Plot")
    city_or_district = Column(String(100), default="General Agro-Zone", index=True)
    soil_type = Column(String(50), default="Loamy")  # Loamy, Clayey, Sandy, etc.
    water_availability = Column(String(50), default="Medium")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farmer = relationship("Farmer", back_populates="farms")
    crops = relationship("Crop", back_populates="farm", cascade="all, delete-orphan")
    diagnoses = relationship("DiseasePrediction", back_populates="farm")


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    crop_name = Column(String(50), nullable=False)  # Tomato, Potato, Corn, etc.
    growth_stage = Column(String(50), default="Growing")  # Vegetative, Flowering, Fruiting, etc.
    previous_crop = Column(String(50), nullable=True)
    status = Column(String(20), default="active")  # 'active', 'harvested'
    planted_at = Column(DateTime, default=datetime.datetime.utcnow)

    farm = relationship("Farm", back_populates="crops")

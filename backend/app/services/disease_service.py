"""
AgriSmart AI - Disease & Cureness Service
Coordinates:
- Model 1: Disease image diagnosis
- Model 2: Cureness treatment and recovery planning
- Database persistence for historical tracking
"""

import os
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from model.fake_engine import default_engine
from model.cure_model import cure_model
from model.class_catalog import CLASS_METADATA, ALL_CLASSES
from app.models.diagnosis import DiseasePrediction
from app.config import settings


class DiseaseService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def process_uploaded_image(
        self,
        file_bytes: bytes,
        original_filename: str,
        farm_id: Optional[int] = None,
        growth_stage: Optional[str] = "Growing",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Executes Dual Model Pipeline:
        1. Model 1 identifies disease from leaf image.
        2. Model 2 prescribes cureness plan and recovery probability.
        """
        ext = os.path.splitext(original_filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"

        unique_filename = f"{uuid.uuid4().hex}{ext}"
        saved_path = os.path.join(self.upload_dir, unique_filename)

        with open(saved_path, "wb") as f:
            f.write(file_bytes)

        # Run dual-model inference
        result = default_engine.predict_detailed(saved_path, growth_stage=growth_stage)

        # Persist prediction & cureness plan to database
        record_id = None
        if db is not None:
            cure_plan = result.get("cureness_plan", {})
            db_record = DiseasePrediction(
                farm_id=farm_id,
                image_filename=unique_filename,
                predicted_class=result["predicted_class"],
                confidence=result["confidence"],
                is_healthy=result["is_healthy"],
                severity=result["severity"],
                recovery_chance_pct=result.get("recovery_chance_pct"),
                recovery_timeline=result.get("recovery_timeline"),
                urgency_level=result.get("urgency_level"),
                precaution=result["precaution"],
                organic_remedy=result["organic_remedy"],
                chemical_remedy=result["chemical_remedy"],
                prognosis_summary=cure_plan.get("prognosis_summary")
            )
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            record_id = db_record.id

        result["image_filename"] = unique_filename
        result["saved_record_id"] = record_id
        return result

    def process_file_path(
        self,
        image_path: str,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Direct inference for programmatic path evaluation (Section 4.1).
        """
        result = default_engine.predict_detailed(image_path)

        record_id = None
        if db is not None:
            filename = os.path.basename(image_path)
            cure_plan = result.get("cureness_plan", {})
            db_record = DiseasePrediction(
                image_filename=filename,
                predicted_class=result["predicted_class"],
                confidence=result["confidence"],
                is_healthy=result["is_healthy"],
                severity=result["severity"],
                recovery_chance_pct=result.get("recovery_chance_pct"),
                recovery_timeline=result.get("recovery_timeline"),
                urgency_level=result.get("urgency_level"),
                precaution=result["precaution"],
                organic_remedy=result["organic_remedy"],
                chemical_remedy=result["chemical_remedy"],
                prognosis_summary=cure_plan.get("prognosis_summary")
            )
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            record_id = db_record.id

        result["image_filename"] = os.path.basename(image_path)
        result["saved_record_id"] = record_id
        return result

    def get_direct_cure_plan(
        self,
        disease_class: str,
        crop: Optional[str] = None,
        growth_stage: Optional[str] = "Growing"
    ) -> Dict[str, Any]:
        """
        Direct invocation of Model 2 (Cureness Prescriber).
        """
        return cure_model.predict_cure(
            predicted_class=disease_class,
            crop=crop,
            growth_stage=growth_stage
        )

    def get_catalog_classes(self) -> List[Dict[str, Any]]:
        """Returns the full catalog of ~15-20 shared classes with details"""
        classes_data = []
        for cls_name, meta in CLASS_METADATA.items():
            classes_data.append({
                "class_name": cls_name,
                "crop": meta.get("crop", "Unknown"),
                "disease_name": meta.get("disease_name", "Unknown"),
                "is_healthy": meta.get("is_healthy", False),
                "severity": meta.get("severity", "Medium"),
                "precaution": meta.get("precaution", "")
            })
        return classes_data

    def get_history(self, db: Session, limit: int = 20) -> List[DiseasePrediction]:
        """Fetches recent diagnosis & cureness records"""
        return db.query(DiseasePrediction).order_by(DiseasePrediction.created_at.desc()).limit(limit).all()


disease_service = DiseaseService()

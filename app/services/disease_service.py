"""
AgriSmart AI - Disease & Gemini Pro Advisory Service
Coordinates:
1. Computer Vision model for leaf image disease detection.
2. Google Gemini Pro for disease explanation and cure prompt.
3. Google Gemini Pro for on-demand cureness and recovery planning.
"""

import os
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from model.disease_model import disease_model
from app.services.gemini_service import gemini_advisor
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
        include_cure: bool = False,
        growth_stage: Optional[str] = "Growing",
        language: str = "en",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Flow:
        1. Single CV model predicts disease class from leaf image.
        2. Gemini Pro generates detailed disease description and asks if farmer wants a cure.
        3. If include_cure=True, Gemini Pro provides the step-by-step cure plan.
        """
        ext = os.path.splitext(original_filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"

        unique_filename = f"{uuid.uuid4().hex}{ext}"
        saved_path = os.path.join(self.upload_dir, unique_filename)

        with open(saved_path, "wb") as f:
            f.write(file_bytes)

        # Step 1: CV Model detection
        detection = disease_model.predict_detailed(saved_path)
        predicted_class = detection["predicted_class"]
        crop = detection["crop"]
        is_healthy = detection["is_healthy"]
        severity = detection["severity"]

        # Step 2: Gemini Pro explains disease and asks if user wants cure
        description_info = gemini_advisor.describe_disease(
            disease_name=predicted_class,
            crop=crop,
            severity=severity,
            is_healthy=is_healthy,
            language=language
        )

        # Step 3: Optional cure generation if farmer already requested it
        cure_plan = None
        if include_cure:
            cure_plan = gemini_advisor.generate_cure_plan(
                disease_name=predicted_class,
                crop=crop,
                growth_stage=growth_stage,
                language=language
            )

        # Step 4: Database logging
        record_id = None
        if db is not None:
            db_record = DiseasePrediction(
                farm_id=farm_id,
                image_filename=unique_filename,
                predicted_class=predicted_class,
                confidence=detection["confidence"],
                is_healthy=is_healthy,
                severity=severity,
                disease_description=description_info["description"],
                cure_prompt=description_info["follow_up_prompt"],
                recovery_chance_pct=cure_plan.get("recovery_chance_pct") if cure_plan else None,
                recovery_timeline=cure_plan.get("recovery_timeline") if cure_plan else None,
                organic_treatment=cure_plan.get("organic_treatment") if cure_plan else None,
                chemical_treatment=cure_plan.get("chemical_treatment") if cure_plan else None
            )
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            record_id = db_record.id

        return {
            "predicted_class": predicted_class,
            "confidence": detection["confidence"],
            "is_healthy": is_healthy,
            "crop": crop,
            "disease_name": detection["disease_name"],
            "severity": severity,
            "top_k": detection["top_k"],
            "disease_description": description_info,
            "cure_plan": cure_plan,
            "image_filename": unique_filename,
            "saved_record_id": record_id,
            "architecture": "CV Leaf Classifier + Google Gemini Pro Advisory"
        }

    def process_file_path(
        self,
        image_path: str,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Direct inference for programmatic path evaluation (Section 4.1).
        """
        detection = disease_model.predict_detailed(image_path)
        predicted_class = detection["predicted_class"]

        record_id = None
        if db is not None:
            filename = os.path.basename(image_path)
            db_record = DiseasePrediction(
                image_filename=filename,
                predicted_class=predicted_class,
                confidence=detection["confidence"],
                is_healthy=detection["is_healthy"],
                severity=detection["severity"],
                disease_description=f"Automated test prediction for {predicted_class}."
            )
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            record_id = db_record.id

        detection["saved_record_id"] = record_id
        return detection

    def get_cure_plan(
        self,
        disease_class: str,
        crop: Optional[str] = "Crop",
        growth_stage: Optional[str] = "Growing",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Triggered when the farmer answers 'Yes' to receiving a cure plan.
        """
        return gemini_advisor.generate_cure_plan(
            disease_name=disease_class,
            crop=crop or "Crop",
            growth_stage=growth_stage or "Growing",
            language=language
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

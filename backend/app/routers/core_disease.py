"""
AgriSmart AI - Core Disease Detection & Cureness Router
Provides endpoints for:
- Model 1: Disease Classification
- Model 2: Cureness & Treatment Plan Prescription
Ref: SIH 2026 Problem Statement 1, Page 1 (Section 3.1) & Page 3 (Section 4.1).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.disease_service import disease_service
from app.schemas.disease import (
    DiseasePredictionResponse,
    PathPredictionRequest,
    PathPredictionResponse,
    DirectCureRequest,
    CurenessPlan,
    CatalogResponse
)

router = APIRouter(prefix="/api/v1/disease", tags=["Core Task: Disease Detection & Cureness"])


@router.post(
    "/predict",
    response_model=DiseasePredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Diagnose Disease & Prescribe Cureness Plan (Dual Model)",
    description=(
        "Chains Model 1 (Disease Detection) and Model 2 (Cureness Prescriber).\n"
        "Accepts a leaf image and returns the disease class, confidence, recovery probability, "
        "and specific multi-phase treatment plan."
    )
)
async def predict_disease_image(
    image: UploadFile = File(..., description="Leaf or crop image to diagnose"),
    growth_stage: Optional[str] = Form("Growing", description="Current crop growth stage (e.g. Vegetative, Flowering, Fruiting)"),
    farm_id: Optional[int] = Form(None, description="Optional associated farm ID"),
    db: Session = Depends(get_db)
):
    # Validate content type
    if image.content_type and not (image.content_type.startswith("image/") or image.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a valid image file (JPEG, PNG, WEBP)."
        )

    try:
        content = await image.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        if len(content) > 10 * 1024 * 1024:  # 10 MB limit
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

        result = disease_service.process_uploaded_image(
            file_bytes=content,
            original_filename=image.filename or "leaf.jpg",
            farm_id=farm_id,
            growth_stage=growth_stage,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Inference error: {str(e)}")


@router.post(
    "/cure",
    response_model=CurenessPlan,
    status_code=status.HTTP_200_OK,
    summary="Prescribe Cureness Plan Directly (Model 2)",
    description="Directly queries Model 2 (Cureness Prescriber) for an already diagnosed disease or specific crop condition."
)
def get_cureness_prescription(
    payload: DirectCureRequest
):
    try:
        cure_plan = disease_service.get_direct_cure_plan(
            disease_class=payload.disease_class,
            crop=payload.crop,
            growth_stage=payload.growth_stage
        )
        return cure_plan
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Cure model error: {str(e)}")


@router.post(
    "/internal/predict-path",
    response_model=PathPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluation Predict Interface (By Path)",
    description="Programmatic endpoint matching Section 4.1 submission contract. Takes an image_path on disk and returns strictly the class_label string from Model 1."
)
def predict_disease_by_path(
    payload: PathPredictionRequest,
    db: Session = Depends(get_db)
):
    try:
        result = disease_service.process_file_path(payload.image_path, db=db)
        return PathPredictionResponse(class_label=result["predicted_class"])
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/classes",
    response_model=CatalogResponse,
    summary="Get List of Supported Disease Classes",
    description="Returns all ~15-20 supported crop-disease classes across PlantVillage and PlantDoc with precaution details."
)
def get_supported_classes():
    classes = disease_service.get_catalog_classes()
    return CatalogResponse(total_classes=len(classes), classes=classes)


@router.get(
    "/history",
    summary="Get Recent Diagnosis & Cure History",
    description="Fetches audit history of recently diagnosed leaf images along with prescribed recovery chances and urgency levels."
)
def get_diagnosis_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    records = disease_service.get_history(db, limit=limit)
    return [
        {
            "id": r.id,
            "predicted_class": r.predicted_class,
            "confidence": r.confidence,
            "is_healthy": r.is_healthy,
            "severity": r.severity,
            "recovery_chance_pct": r.recovery_chance_pct,
            "recovery_timeline": r.recovery_timeline,
            "urgency_level": r.urgency_level,
            "precaution": r.precaution,
            "prognosis_summary": r.prognosis_summary,
            "image_filename": r.image_filename,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]

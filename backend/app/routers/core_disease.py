"""
AgriSmart AI - Core Disease Detection & Gemini Pro Advisory Router
Workflow:
1. Computer Vision model identifies disease from leaf image.
2. Gemini Pro generates disease description and prompts: "Would you like a cure plan?"
3. If farmer confirms (or calls /cure), Gemini Pro delivers the tailored cure plan.
Ref: SIH 2026 Problem Statement 1, Page 1 (Section 3.1) & Page 3 (Section 4.1).
"""

from typing import List, Optional
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.disease_service import disease_service
from app.schemas.disease import (
    DiseasePredictionResponse,
    PathPredictionRequest,
    PathPredictionResponse,
    CureRequest,
    GeminiCurePlan,
    CatalogResponse
)

router = APIRouter(prefix="/api/v1/disease", tags=["Core Task: Disease Detection & Gemini Advisory"])


@router.post(
    "/predict",
    response_model=DiseasePredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Diagnose Leaf Image (CV Detection + Gemini Pro Description)",
    description=(
        "1. Single CV model predicts disease class and confidence from leaf image.\n"
        "2. Gemini Pro generates an insightful disease explanation and asks if the farmer wants a cure plan.\n"
        "3. If `include_cure=True`, Gemini Pro also includes the full recovery and treatment plan immediately."
    )
)
async def predict_disease_image(
    image: UploadFile = File(..., description="Leaf image to classify"),
    include_cure: bool = Form(False, description="Set True to generate cure plan immediately, or False to receive description and prompt first"),
    growth_stage: Optional[str] = Form("Growing", description="Current crop growth stage (e.g. Vegetative, Flowering, Fruiting)"),
    language: Optional[str] = Form("en", description="Preferred response language (en, hi, mr, etc.)"),
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
        content = bytearray()
        while chunk := await image.read(1024 * 1024):
            content.extend(chunk)
            if len(content) > 10 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        content = bytes(content)
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        result = disease_service.process_uploaded_image(
            file_bytes=content,
            original_filename=image.filename or "leaf.jpg",
            farm_id=farm_id,
            include_cure=include_cure,
            growth_stage=growth_stage,
            language=language,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Analysis error: {str(e)}")


@router.post(
    "/cure",
    response_model=GeminiCurePlan,
    status_code=status.HTTP_200_OK,
    summary="Get Step-by-Step Cure Plan (Gemini Pro)",
    description="Invoked when the farmer responds 'Yes' to receiving a cure plan. Gemini Pro delivers dosages, recovery timelines, and organic/chemical treatments."
)
def get_cure_plan(
    payload: CureRequest
):
    try:
        cure_plan = disease_service.get_cure_plan(
            disease_class=payload.disease_class,
            crop=payload.crop,
            growth_stage=payload.growth_stage,
            language=payload.language
        )
        return cure_plan
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Cure generation error: {str(e)}")


@router.post(
    "/internal/predict-path",
    response_model=PathPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluation Predict Interface (By Path)",
    description="Programmatic endpoint matching Section 4.1 submission contract. Takes an image_path on disk and returns strictly the class_label string."
)
def predict_disease_by_path(
    payload: PathPredictionRequest,
    db: Session = Depends(get_db)
):
    from app.config import settings

    # Security: restrict path access to the configured uploads directory only
    allowed_dir = os.path.abspath(settings.UPLOAD_DIR)
    requested_path = os.path.abspath(payload.image_path)
    if not requested_path.startswith(allowed_dir + os.sep) and requested_path != allowed_dir:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Path must be within the configured uploads directory."
        )

    try:
        result = disease_service.process_file_path(requested_path, db=db)
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
    summary="Get Recent Diagnosis History",
    description="Fetches audit history of recently diagnosed leaf images."
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
            "disease_description": r.disease_description,
            "cure_prompt": r.cure_prompt,
            "recovery_chance_pct": r.recovery_chance_pct,
            "recovery_timeline": r.recovery_timeline,
            "image_filename": r.image_filename,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]

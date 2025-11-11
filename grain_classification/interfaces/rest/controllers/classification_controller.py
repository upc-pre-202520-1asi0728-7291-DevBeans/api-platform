from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from grain_classification.application.internal.classification_service import ClassificationApplicationService
from grain_classification.domain.model.valueobjetcs.quality_models import CNN_COLOR_CLASSES
from grain_classification.domain.services.grading_service import QualityGradingService
from grain_classification.infrastructure.cv_service import CVService
from grain_classification.infrastructure.ml_predictor_service import MLPredictorService
from shared.domain.database import get_db


# --- Inyección de Dependencias (Usando Depends de FastAPI) ---

# (Estos servicios ahora son "singletons" para eficiencia)
def get_ml_predictor() -> MLPredictorService:
    model_path = "grain_classification/infrastructure/ml_models/defect_detector.h5"
    if not hasattr(get_ml_predictor, "singleton"):
        get_ml_predictor.singleton = MLPredictorService(model_path, CNN_COLOR_CLASSES)
    return get_ml_predictor.singleton


def get_cv_service() -> CVService:
    if not hasattr(get_cv_service, "singleton"):
        get_cv_service.singleton = CVService()
    return get_cv_service.singleton


def get_grading_service() -> QualityGradingService:
    if not hasattr(get_grading_service, "singleton"):
        get_grading_service.singleton = QualityGradingService()
    return get_grading_service.singleton


def get_classification_service(
        db: Session = Depends(get_db),  # <-- Usando tu get_db
        cv: CVService = Depends(get_cv_service),
        ml: MLPredictorService = Depends(get_ml_predictor),
        grading: QualityGradingService = Depends(get_grading_service)
) -> ClassificationApplicationService:
    return ClassificationApplicationService(db, cv, ml, grading)


# --- Fin de Inyección ---

router = APIRouter(
    prefix="/api/v1/classification",
    tags=["Grain Classification"]
)


# --- Definición de Recursos (DTOs) ---
class ClassificationSessionResponse(BaseModel):
    """Recurso de respuesta para una sesión completada"""
    id: int
    session_id_vo: str
    coffee_lot_id: int
    user_id: int
    status: str
    total_grains_analyzed: int
    processing_time_seconds: float | None
    classification_result: dict  # El reporte JSON
    created_at: datetime
    completed_at: datetime | None

    class Config:
        orm_mode = True  # Permite a Pydantic leer desde el objeto SQLAlchemy


@router.post("/session", response_model=ClassificationSessionResponse, status_code=201)
async def start_and_process_classification_session(
        coffee_lot_id: int = Form(...),
        image: UploadFile = File(...),
        # user_id: int = Depends(get_current_user_id), # TODO: Integrar con IAM
        service: ClassificationApplicationService = Depends(get_classification_service)
):
    """
    Inicia, procesa y completa una sesión de clasificación a partir de una sola imagen.
    Guarda los resultados en la base de datos.
    """
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Formato de imagen no válido. Usar JPG o PNG.")

    image_bytes = await image.read()

    try:
        session = service.start_classification_session(
            coffee_lot_id=coffee_lot_id,
            image_bytes=image_bytes,
            user_id=1  # Reemplazar con ID de usuario autenticado
        )

        if session.status == "FAILED":
            raise HTTPException(status_code=500,
                                detail=f"Clasificación fallida: {session.classification_result.get('error')}")

        return session

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error interno durante la clasificación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor de clasificación.")
# traceability_certification/domain/model/commands/create_certification_command.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class CreateCertificationCommand(BaseModel):
    """
    Comando para crear un certificado de trazabilidad inmutable.

    Captura la intención de certificar una clasificación completada.
    """
    classification_session_id: int = Field(..., description="ID de la sesión de clasificación")
    coffee_lot_id: int = Field(..., description="ID del lote de café")

    # Datos de calidad
    quality_score: float = Field(..., ge=0, le=100, description="Puntaje de calidad (0-100)")
    quality_category: str = Field(..., description="Categoría de calidad (Specialty, Premium, etc.)")
    total_grains_analyzed: int = Field(..., gt=0, description="Total de granos analizados")

    # Metadatos completos de la clasificación (para generar hash)
    classification_metadata: Dict[str, Any] = Field(..., description="Metadatos completos de clasificación")

    # Opcionales
    make_public: bool = Field(default=True, description="Si el certificado es público")
    certification_notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    expires_in_days: Optional[int] = Field(None, gt=0, description="Días hasta expiración (opcional)")

    class Config:
        json_schema_extra = {
            "example": {
                "classification_session_id": 123,
                "coffee_lot_id": 45,
                "quality_score": 86.5,
                "quality_category": "Specialty",
                "total_grains_analyzed": 1,
                "classification_metadata": {
                    "session_id": "SESS-ABC123",
                    "final_score": 0.865,
                    "final_category": "Specialty",
                    "timestamp": "2025-11-28T10:00:00Z"
                },
                "make_public": True
            }
        }
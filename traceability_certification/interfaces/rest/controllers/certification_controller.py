# traceability_certification/interfaces/rest/controllers/certification_controller.py

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, status, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from shared.domain.database import get_db
from traceability_certification.application.internal.certification_command_service import CertificationCommandService
from traceability_certification.application.internal.certification_query_service import CertificationQueryService
from traceability_certification.domain.model.commands.create_certification_command import CreateCertificationCommand
from traceability_certification.domain.model.queries.verify_certification_query import (
    VerifyCertificationByHashQuery,
    VerifyCertificationByTokenQuery,
    GetCertificationByIdQuery,
    GetCertificationsByLotQuery
)

router = APIRouter(prefix="/api/v1/certifications", tags=["Traceability & Certification"])


# ============ DTOs / Resources ============

class CertificationResource(BaseModel):
    """DTO de respuesta para un certificado"""
    id: int
    certification_id: str
    certification_hash: str
    classification_session_id: int
    coffee_lot_id: int
    quality_score: float
    quality_category: str
    total_grains_analyzed: int
    verification_token: str
    status: str
    is_public: bool
    certified_at: datetime
    expires_at: Optional[datetime]
    certification_notes: Optional[str]

    class Config:
        from_attributes = True


class VerificationResponse(BaseModel):
    """DTO de respuesta para verificación"""
    verified: bool
    certification_id: Optional[str] = None
    certification_hash: Optional[str] = None
    quality_score: Optional[float] = None
    quality_category: Optional[str] = None
    certified_at: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None


class PublicVerificationResponse(BaseModel):
    """DTO de respuesta para verificación pública (sin datos sensibles)"""
    certification_id: str
    certification_hash: str
    quality_score: float
    quality_category: str
    total_grains_analyzed: int
    certified_at: str
    status: str
    is_valid: bool


class RevokeCertificationRequest(BaseModel):
    """DTO para revocar certificado"""
    reason: str = Field(..., min_length=10, max_length=500)


# ============ Dependency Injection ============

def get_command_service(db: Session = Depends(get_db)) -> CertificationCommandService:
    return CertificationCommandService(db)


def get_query_service(db: Session = Depends(get_db)) -> CertificationQueryService:
    return CertificationQueryService(db)


# ============ Endpoints ============

@router.post("", response_model=CertificationResource, status_code=status.HTTP_201_CREATED)
async def create_certification(
        command: CreateCertificationCommand = Body(...),
        service: CertificationCommandService = Depends(get_command_service)
):
    """
    Crea un certificado de trazabilidad inmutable para una clasificación.

    Genera automáticamente:
    - Hash SHA-256 inmutable
    - ID de certificado único (CERT-...)
    - Token de verificación pública
    """
    certification = service.handle_create_certification(command)
    return CertificationResource.model_validate(certification)


@router.get("/verify/hash/{certification_hash}", response_model=VerificationResponse)
async def verify_certification_by_hash(
        certification_hash: str = Path(..., min_length=64, max_length=64),
        service: CertificationQueryService = Depends(get_query_service)
):
    """
    Verifica la autenticidad de un certificado usando su hash.

    Verifica:
    - Existencia del hash en la base de datos
    - Integridad del hash (recalcula y compara)
    - Validez del certificado (no revocado, no expirado)
    """
    query = VerifyCertificationByHashQuery(certification_hash=certification_hash)
    result = service.handle_verify_by_hash(query)
    return VerificationResponse(**result)


@router.get("/verify/token/{verification_token}", response_model=PublicVerificationResponse)
async def verify_certification_by_token(
        verification_token: str = Path(..., min_length=12, max_length=12),
        service: CertificationQueryService = Depends(get_query_service)
):
    """
    Verifica un certificado usando el token de verificación pública.

    Endpoint público (sin autenticación) para QR codes.
    Retorna solo datos no sensibles.
    """
    query = VerifyCertificationByTokenQuery(verification_token=verification_token)
    result = service.handle_verify_by_token(query)
    return PublicVerificationResponse(**result)


@router.get("/{certification_id}", response_model=CertificationResource)
async def get_certification_by_id(
        certification_id: str = Path(..., description="ID del certificado (CERT-...)"),
        service: CertificationQueryService = Depends(get_query_service)
):
    """Obtiene un certificado específico por su ID"""
    query = GetCertificationByIdQuery(certification_id=certification_id)
    certification = service.handle_get_by_id(query)
    return CertificationResource.model_validate(certification)


@router.get("/lot/{coffee_lot_id}", response_model=List[CertificationResource])
async def get_certifications_by_lot(
        coffee_lot_id: int = Path(..., gt=0, description="ID del lote de café"),
        service: CertificationQueryService = Depends(get_query_service)
):
    """Obtiene todos los certificados de un lote de café"""
    query = GetCertificationsByLotQuery(coffee_lot_id=coffee_lot_id)
    certifications = service.handle_get_by_lot(query)
    return [CertificationResource.model_validate(cert) for cert in certifications]


@router.patch("/{certification_id}/revoke", response_model=CertificationResource)
async def revoke_certification(
        certification_id: str = Path(..., description="ID del certificado a revocar"),
        request: RevokeCertificationRequest = Body(...),
        service: CertificationCommandService = Depends(get_command_service)
):
    """
    Revoca un certificado existente.

    Un certificado revocado permanece en la base de datos, pero ya no se considera válido.
    """
    certification = service.handle_revoke_certification(certification_id, request.reason)
    return CertificationResource.model_validate(certification)


@router.get("", response_model=List[CertificationResource])
async def get_all_public_certifications(
        service: CertificationQueryService = Depends(get_query_service)
):
    """
    Obtiene todos los certificados públicos.

    Endpoint sin autenticación para transparencia pública.
    """
    certifications = service.get_all_public_certifications()
    return [CertificationResource.model_validate(cert) for cert in certifications]
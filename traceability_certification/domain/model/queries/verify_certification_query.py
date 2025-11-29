# traceability_certification/domain/model/queries/verify_certification_query.py

from pydantic import BaseModel, Field


class VerifyCertificationByHashQuery(BaseModel):
    """Query para verificar un certificado por su hash"""
    certification_hash: str = Field(..., min_length=64, max_length=64)


class VerifyCertificationByTokenQuery(BaseModel):
    """Query para verificar un certificado por su token público"""
    verification_token: str = Field(..., min_length=12, max_length=12)


class GetCertificationByIdQuery(BaseModel):
    """Query para obtener un certificado por su ID"""
    certification_id: str = Field(...)


class GetCertificationsByLotQuery(BaseModel):
    """Query para obtener todos los certificados de un lote"""
    coffee_lot_id: int = Field(..., gt=0)
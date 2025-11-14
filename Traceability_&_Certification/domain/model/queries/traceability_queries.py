from pydantic import BaseModel
from typing import Optional


class GetTraceabilityRecordQuery(BaseModel):
    """Query para obtener un registro de trazabilidad"""
    record_id: int


class GetTraceabilityByLotQuery(BaseModel):
    """Query para obtener todos los registros de un lote"""
    coffee_lot_id: int


class GetTraceabilityByRecordNumberQuery(BaseModel):
    """Query para obtener registro por número"""
    record_number: str


class GetCertificateQuery(BaseModel):
    """Query para obtener un certificado"""
    certificate_id: int


class GetCertificateByNumberQuery(BaseModel):
    """Query para obtener certificado por número"""
    certificate_number: str


class GetCertificatesByLotQuery(BaseModel):
    """Query para obtener certificados de un lote"""
    coffee_lot_id: int


class VerifyBlockchainHashQuery(BaseModel):
    """Query para verificar un hash en blockchain"""
    blockchain_hash: str
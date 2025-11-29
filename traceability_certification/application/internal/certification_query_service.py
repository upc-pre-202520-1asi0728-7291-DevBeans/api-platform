# traceability_certification/application/internal/certification_query_service.py

from typing import Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from traceability_certification.domain.model.aggregates.certification_record import CertificationRecord
from traceability_certification.domain.model.queries.verify_certification_query import (
    VerifyCertificationByHashQuery,
    VerifyCertificationByTokenQuery,
    GetCertificationByIdQuery,
    GetCertificationsByLotQuery
)
from traceability_certification.domain.services.hash_service import HashService
from traceability_certification.infrastructure.persistence.database.repositories.certification_repository import \
    CertificationRepository


class CertificationQueryService:
    """
    Servicio de aplicación para consultas de certificación
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = CertificationRepository(db)
        self.hash_service = HashService()

    def handle_verify_by_hash(self, query: VerifyCertificationByHashQuery) -> Dict[str, Any]:
        """
        Verifica un certificado por su hash inmutable.
        Retorna información de verificación.
        """
        certification = self.repository.find_by_hash(query.certification_hash)

        if not certification:
            return {
                'verified': False,
                'message': 'Certification hash not found',
                'certification_hash': query.certification_hash
            }

        # Verificar integridad recalculando el hash
        is_valid = self.hash_service.verify_hash(
            certification.classification_metadata,
            query.certification_hash
        )

        return {
            'verified': is_valid and certification.is_valid(),
            'certification_id': certification.certification_id,
            'certification_hash': certification.certification_hash,
            'quality_score': certification.quality_score,
            'quality_category': certification.quality_category,
            'total_grains_analyzed': certification.total_grains_analyzed,
            'certified_at': certification.certified_at.isoformat() if certification.certified_at else None,
            'status': certification.status.value,
            'is_public': certification.is_public,
            'expires_at': certification.expires_at.isoformat() if certification.expires_at else None,
            'hash_integrity_check': is_valid
        }

    def handle_verify_by_token(self, query: VerifyCertificationByTokenQuery) -> Dict[str, Any]:
        """
        Verifica un certificado por su token de verificación pública.
        Usado para QR codes y verificación sin autenticación.
        """
        certification = self.repository.find_by_verification_token(query.verification_token)

        if not certification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Verification token not found: {query.verification_token}"
            )

        # Retornar solo datos públicos
        return certification.get_public_verification_data()

    def handle_get_by_id(self, query: GetCertificationByIdQuery) -> CertificationRecord:
        """Obtiene un certificado por su ID legible"""
        certification = self.repository.find_by_certification_id(query.certification_id)

        if not certification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certification not found: {query.certification_id}"
            )

        return certification

    def handle_get_by_lot(self, query: GetCertificationsByLotQuery) -> list[type[CertificationRecord]]:
        """Obtiene todos los certificados de un lote de café"""
        certifications = self.repository.find_by_coffee_lot(query.coffee_lot_id)

        if not certifications:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No certifications found for coffee lot {query.coffee_lot_id}"
            )

        return certifications

    def get_all_public_certifications(self) -> list[type[CertificationRecord]]:
        """Obtiene todos los certificados públicos (sin autenticación)"""
        return self.repository.find_public_certifications()
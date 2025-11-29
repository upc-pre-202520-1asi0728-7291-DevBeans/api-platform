# traceability_certification/application/internal/certification_command_service.py

import shortuuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta, UTC
from typing import Optional

from traceability_certification.domain.model.aggregates.certification_record import CertificationRecord
from traceability_certification.domain.model.commands.create_certification_command import CreateCertificationCommand
from traceability_certification.domain.services.hash_service import HashService
from traceability_certification.infrastructure.persistence.database.repositories.certification_repository import \
    CertificationRepository


class CertificationCommandService:
    """
    Servicio de aplicación para comandos de certificación
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = CertificationRepository(db)
        self.hash_service = HashService()

    def handle_create_certification(self, command: CreateCertificationCommand) -> CertificationRecord:
        """
        Crea un certificado de trazabilidad inmutable para una clasificación.

        Proceso:
        1. Valida que no exista certificado previo
        2. Genera hash inmutable basado en datos de clasificación
        3. Genera token de verificación pública
        4. Persiste el certificado
        """
        # 1. Validar que no exista certificado previo para esta sesión
        existing = self.repository.find_by_classification_session(command.classification_session_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Certification already exists for session {command.classification_session_id}"
            )

        # 2. Preparar datos para el hash
        hash_data = {
            'session_id': command.classification_metadata.get('session_id_vo'),
            'coffee_lot_id': command.coffee_lot_id,
            'final_score': command.quality_score / 100,  # Normalizar a 0-1
            'final_category': command.quality_category,
            'total_grains_analyzed': command.total_grains_analyzed,
            'timestamp': command.classification_metadata.get('completed_at') or datetime.now(UTC).isoformat(),
            'processing_time_seconds': command.classification_metadata.get('processing_time_seconds')
        }

        # 3. Generar hash inmutable
        certification_hash = self.hash_service.generate_certification_hash(hash_data)

        # 4. Verificar que el hash sea único (extremadamente improbable duplicado, pero por seguridad)
        if self.repository.exists_by_hash(certification_hash):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hash collision detected. This is extremely rare - please retry."
            )

        # 5. Generar ID de certificado legible
        certification_id = f"CERT-{shortuuid.uuid()[:12].upper()}"

        # 6. Generar token de verificación pública
        verification_token = self.hash_service.generate_verification_token()

        # 7. Calcular fecha de expiración si aplica
        expires_at: Optional[datetime] = None
        if command.expires_in_days:
            expires_at = datetime.now(UTC) + timedelta(days=command.expires_in_days)

        # 8. Crear el agregado
        certification = CertificationRecord(
            certification_id=certification_id,
            classification_session_id=command.classification_session_id,
            coffee_lot_id=command.coffee_lot_id,
            certification_hash=certification_hash,
            quality_score=command.quality_score,
            quality_category=command.quality_category,
            total_grains_analyzed=command.total_grains_analyzed,
            classification_metadata=command.classification_metadata,
            verification_token=verification_token
        )

        # Configurar opcionales
        certification.is_public = command.make_public
        certification.certification_notes = command.certification_notes
        certification.expires_at = expires_at

        # 9. Persistir
        return self.repository.save(certification)

    def handle_revoke_certification(self, certification_id: str, reason: str) -> CertificationRecord:
        """Revoca un certificado existente"""
        certification = self.repository.find_by_certification_id(certification_id)

        if not certification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certification {certification_id} not found"
            )

        if certification.status.value == "REVOKED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Certification is already revoked"
            )

        certification.revoke(reason)
        return self.repository.save(certification)
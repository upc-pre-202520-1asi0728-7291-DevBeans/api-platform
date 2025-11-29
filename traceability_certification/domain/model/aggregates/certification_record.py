# traceability_certification/domain/model/aggregates/certification_record.py

import enum
from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey, JSON, Boolean

from shared.domain.aggregate_root import AuditableAbstractAggregateRoot


class CertificationStatus(str, enum.Enum):
    """Estados del certificado de trazabilidad"""
    ACTIVE = "ACTIVE"
    VERIFIED = "VERIFIED"
    REVOKED = "REVOKED"


class CertificationRecord(AuditableAbstractAggregateRoot):
    """
    Agregado Root - Registro de Certificación con Hash Inmutable

    Representa la certificación de trazabilidad de una clasificación,
    incluyendo el hash criptográfico inmutable que garantiza la autenticidad.
    """
    __tablename__ = "certification_records"

    # Identificador único del certificado
    certification_id = Column(String(20), unique=True, nullable=False, index=True)

    # Referencias a otros bounded contexts
    classification_session_id = Column(Integer, ForeignKey("classification_sessions.id"), nullable=False, index=True)
    coffee_lot_id = Column(Integer, ForeignKey("coffee_lots.id"), nullable=False, index=True)

    # Hash inmutable (núcleo de la trazabilidad)
    certification_hash = Column(String(64), unique=True, nullable=False, index=True)

    # Datos de certificación
    quality_score = Column(Float, nullable=False)
    quality_category = Column(String(50), nullable=False)
    total_grains_analyzed = Column(Integer, nullable=False)

    # Metadatos de clasificación (almacenados para regenerar hash si es necesario)
    classification_metadata = Column(JSON, nullable=False)

    # Token de verificación pública (para QR codes)
    verification_token = Column(String(12), unique=True, nullable=False, index=True)

    # Estado y validez
    status = Column(SQLEnum(CertificationStatus), default=CertificationStatus.ACTIVE, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)

    # Timestamps de certificación
    certified_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Opcional: para certificados temporales

    # Información adicional
    certification_notes = Column(String(500), nullable=True)

    def __init__(
            self,
            certification_id: str,
            classification_session_id: int,
            coffee_lot_id: int,
            certification_hash: str,
            quality_score: float,
            quality_category: str,
            total_grains_analyzed: int,
            classification_metadata: dict,
            verification_token: str,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.certification_id = certification_id
        self.classification_session_id = classification_session_id
        self.coffee_lot_id = coffee_lot_id
        self.certification_hash = certification_hash
        self.quality_score = quality_score
        self.quality_category = quality_category
        self.total_grains_analyzed = total_grains_analyzed
        self.classification_metadata = classification_metadata
        self.verification_token = verification_token
        self.status = CertificationStatus.ACTIVE
        self.is_public = True

    def revoke(self, reason: str) -> None:
        """Revoca el certificado (marca como inválido)"""
        self.status = CertificationStatus.REVOKED
        self.certification_notes = f"Revoked: {reason}"

    def verify(self) -> None:
        """Marca el certificado como verificado externamente"""
        if self.status == CertificationStatus.ACTIVE:
            self.status = CertificationStatus.VERIFIED

    def is_valid(self) -> bool:
        """Verifica si el certificado es válido"""
        if self.status == CertificationStatus.REVOKED:
            return False

        if self.expires_at and datetime.now(UTC) > self.expires_at:
            return False

        return True

    def get_public_verification_data(self) -> dict:
        """
        Retorna datos públicos para verificación (sin información sensible).
        Usado para QR codes y verificación pública.
        """
        return {
            'certification_id': self.certification_id,
            'certification_hash': self.certification_hash,
            'quality_score': self.quality_score,
            'quality_category': self.quality_category,
            'total_grains_analyzed': self.total_grains_analyzed,
            'certified_at': self.certified_at.isoformat() if self.certified_at else None,
            'status': self.status.value,
            'is_valid': self.is_valid()
        }
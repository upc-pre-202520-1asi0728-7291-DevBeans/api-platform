import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum as SQLEnum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from shared.domain.database import Base


class CertificateType(str, enum.Enum):
    ORGANIC = "ORGANIC"
    FAIR_TRADE = "FAIR_TRADE"
    QUALITY = "QUALITY"
    ORIGIN = "ORIGIN"
    SPECIALTY = "SPECIALTY"
    SUSTAINABILITY = "SUSTAINABILITY"


class CertificateStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    PENDING = "PENDING"


class Certificate(Base):
    """
    Entidad Certificate - Certificados digitales para lotes de café
    """
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)

    # Identificación
    certificate_number = Column(String(100), unique=True, nullable=False, index=True)
    traceability_record_id = Column(Integer, ForeignKey("traceability_records.id"), nullable=False)
    coffee_lot_id = Column(Integer, ForeignKey("coffee_lots.id"), nullable=False)

    # Tipo y estado
    certificate_type = Column(SQLEnum(CertificateType), nullable=False)
    status = Column(SQLEnum(CertificateStatus), default=CertificateStatus.PENDING)

    # Información del certificado
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Fechas
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)

    # Entidad emisora
    issuing_authority = Column(String(255), nullable=False)
    issuing_authority_contact = Column(String(255), nullable=True)

    # Datos adicionales
    certification_criteria = Column(JSON, nullable=True)
    test_results = Column(JSON, nullable=True)

    # Archivos
    pdf_url = Column(String(500), nullable=True)
    qr_code_url = Column(String(500), nullable=True)

    # Hash de verificación
    verification_hash = Column(String(255), nullable=False, index=True)

    # Blockchain
    blockchain_hash = Column(String(255), nullable=True)
    blockchain_transaction_id = Column(String(255), nullable=True)

    # Auditoría
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    traceability_record = relationship("TraceabilityRecord", back_populates="certificates")

    def is_valid(self) -> bool:
        """Verifica si el certificado es válido"""
        if self.status != CertificateStatus.ACTIVE:
            return False
        if self.expiry_date and self.expiry_date < date.today():
            return False
        return True

    def expire(self) -> None:
        """Marca el certificado como expirado"""
        self.status = CertificateStatus.EXPIRED

    def revoke(self) -> None:
        """Revoca el certificado"""
        self.status = CertificateStatus.REVOKED

    def activate(self) -> None:
        """Activa el certificado"""
        self.status = CertificateStatus.ACTIVE

    def add_blockchain_data(self, blockchain_hash: str, transaction_id: str) -> None:
        """Registra datos de blockchain"""
        self.blockchain_hash = blockchain_hash
        self.blockchain_transaction_id = transaction_id
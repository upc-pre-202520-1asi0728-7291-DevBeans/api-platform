import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from shared.domain.aggregate_root import AuditableAbstractAggregateRoot


class RecordType(str, enum.Enum):
    HARVEST = "HARVEST"
    PROCESSING = "PROCESSING"
    QUALITY_CHECK = "QUALITY_CHECK"
    STORAGE = "STORAGE"
    CERTIFICATION = "CERTIFICATION"
    SHIPMENT = "SHIPMENT"


class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class TraceabilityRecord(AuditableAbstractAggregateRoot):
    """
    Agregado TraceabilityRecord - Gestiona registros de trazabilidad
    """
    __tablename__ = "traceability_records"

    # Identificación
    record_number = Column(String(100), unique=True, nullable=False, index=True)
    coffee_lot_id = Column(Integer, ForeignKey("coffee_lots.id"), nullable=False)

    # Tipo de registro
    record_type = Column(SQLEnum(RecordType), nullable=False)
    event_description = Column(Text, nullable=False)

    # Datos del evento
    event_date = Column(DateTime, nullable=False)
    location = Column(String(255), nullable=True)
    responsible_person = Column(String(200), nullable=True)

    # Datos adicionales (flexible JSON)
    metadata = Column(JSON, nullable=True)

    # Verificación
    verification_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING)
    verified_by = Column(String(200), nullable=True)
    verification_date = Column(DateTime, nullable=True)

    # Blockchain
    blockchain_hash = Column(String(255), nullable=True, index=True)
    blockchain_transaction_id = Column(String(255), nullable=True)

    # QR Code (guardado como data URI base64)
    qr_code_data = Column(Text, nullable=True)

    # Relaciones
    certificates = relationship("Certificate", back_populates="traceability_record", cascade="all, delete-orphan")

    def __init__(self, record_number: str, coffee_lot_id: int, record_type: RecordType,
                 event_description: str, event_date: datetime, location: str = None,
                 responsible_person: str = None, metadata: dict = None):
        super().__init__()
        self.record_number = record_number
        self.coffee_lot_id = coffee_lot_id
        self.record_type = record_type
        self.event_description = event_description
        self.event_date = event_date
        self.location = location
        self.responsible_person = responsible_person
        self.metadata = metadata
        self.verification_status = VerificationStatus.PENDING

    def verify(self, verified_by: str) -> None:
        """Marca el registro como verificado"""
        self.verification_status = VerificationStatus.VERIFIED
        self.verified_by = verified_by
        self.verification_date = datetime.now()

    def reject(self, verified_by: str) -> None:
        """Rechaza el registro"""
        self.verification_status = VerificationStatus.REJECTED
        self.verified_by = verified_by
        self.verification_date = datetime.now()

    def add_blockchain_data(self, blockchain_hash: str, transaction_id: str) -> None:
        """Registra datos de blockchain"""
        self.blockchain_hash = blockchain_hash
        self.blockchain_transaction_id = transaction_id

    def set_qr_code(self, qr_data: str) -> None:
        """Establece los datos del código QR (base64)"""
        self.qr_code_data = qr_data

    def is_verified(self) -> bool:
        """Verifica si el registro está verificado"""
        return self.verification_status == VerificationStatus.VERIFIED
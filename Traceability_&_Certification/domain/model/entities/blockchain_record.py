from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from shared.domain.database import Base


class BlockchainRecord(Base):
    """
    Entidad BlockchainRecord - Registro de transacciones en blockchain
    """
    __tablename__ = "blockchain_records"

    id = Column(Integer, primary_key=True, index=True)

    # Identificación
    record_hash = Column(String(255), unique=True, nullable=False, index=True)
    previous_hash = Column(String(255), nullable=True)

    # Datos del registro
    data = Column(JSON, nullable=False)
    data_hash = Column(String(255), nullable=False)

    # Metadata
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    block_number = Column(Integer, nullable=True)

    # Blockchain info
    transaction_id = Column(String(255), nullable=True, index=True)
    blockchain_network = Column(String(50), default="INTERNAL", nullable=False)

    # Referencia al registro de trazabilidad
    reference_type = Column(String(50), nullable=False)  # 'traceability', 'certificate'
    reference_id = Column(Integer, nullable=False)

    # Verificación
    verified = Column(Integer, default=0, nullable=False)  # 0=no verificado, 1=verificado
    verification_count = Column(Integer, default=0, nullable=False)

    # Auditoría
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    def verify_integrity(self) -> bool:
        """Verifica la integridad del registro"""
        import hashlib
        import json

        # Calcular hash de los datos
        data_str = json.dumps(self.data, sort_keys=True)
        calculated_hash = hashlib.sha256(data_str.encode()).hexdigest()

        return calculated_hash == self.data_hash

    def increment_verification(self) -> None:
        """Incrementa el contador de verificaciones"""
        self.verification_count += 1
        if self.verification_count >= 3:
            self.verified = 1
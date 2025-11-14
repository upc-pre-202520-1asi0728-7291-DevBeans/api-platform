import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from traceability_certification.domain.model.entities.blockchain_record import BlockchainRecord


class BlockchainService:
    """
    Servicio para gestión de blockchain interno (simulado)
    Implementa una cadena de bloques simple para inmutabilidad de datos
    """

    def __init__(self, db: Session):
        self.db = db

    def register_data(self, data: Dict[str, Any], reference_type: str, reference_id: int) -> BlockchainRecord:
        """
        Registra datos en el blockchain interno
        """
        # Calcular hash de los datos
        data_hash = self._calculate_hash(data)

        # Obtener hash del bloque anterior
        previous_record = self._get_last_record()
        previous_hash = previous_record.record_hash if previous_record else "0" * 64

        # Calcular hash del nuevo registro (incluyendo hash anterior para cadena)
        block_data = {
            "data_hash": data_hash,
            "previous_hash": previous_hash,
            "timestamp": datetime.now().isoformat(),
            "reference_type": reference_type,
            "reference_id": reference_id
        }
        record_hash = self._calculate_hash(block_data)

        # Crear registro
        blockchain_record = BlockchainRecord(
            record_hash=record_hash,
            previous_hash=previous_hash,
            data=data,
            data_hash=data_hash,
            timestamp=datetime.now(),
            reference_type=reference_type,
            reference_id=reference_id,
            blockchain_network="INTERNAL"
        )

        self.db.add(blockchain_record)
        self.db.commit()
        self.db.refresh(blockchain_record)

        return blockchain_record

    def verify_chain_integrity(self) -> tuple[bool, Optional[str]]:
        """
        Verifica la integridad completa de la cadena de bloques
        """
        records = self.db.query(BlockchainRecord).order_by(BlockchainRecord.id).all()

        for i, record in enumerate(records):
            # Verificar integridad de datos
            if not record.verify_integrity():
                return False, f"Record {record.id} data integrity failed"

            # Verificar enlace con bloque anterior
            if i > 0:
                if record.previous_hash != records[i-1].record_hash:
                    return False, f"Record {record.id} chain link broken"

        return True, "Chain integrity verified"

    def verify_record(self, record_hash: str) -> Optional[BlockchainRecord]:
        """
        Verifica y recupera un registro específico por su hash
        """
        record = self.db.query(BlockchainRecord).filter(
            BlockchainRecord.record_hash == record_hash
        ).first()

        if record and record.verify_integrity():
            record.increment_verification()
            self.db.commit()
            return record

        return None

    def get_record_by_reference(self, reference_type: str, reference_id: int) -> Optional[BlockchainRecord]:
        """
        Obtiene el registro de blockchain por referencia
        """
        return self.db.query(BlockchainRecord).filter(
            BlockchainRecord.reference_type == reference_type,
            BlockchainRecord.reference_id == reference_id
        ).first()

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """
        Calcula hash SHA-256 de los datos
        """
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _get_last_record(self) -> Optional[BlockchainRecord]:
        """
        Obtiene el último registro de la cadena
        """
        return self.db.query(BlockchainRecord).order_by(
            BlockchainRecord.id.desc()
        ).first()


class ExternalBlockchainService:
    """
    Servicio para integración con blockchain externo (Ethereum, Hyperledger, etc.)
    Este es un placeholder para futuras implementaciones
    """

    def __init__(self, network: str = "ethereum", provider_url: Optional[str] = None):
        self.network = network
        self.provider_url = provider_url or "http://localhost:8545"
        # Aquí se inicializaría la conexión con Web3 u otro cliente

    async def register_on_chain(self, data_hash: str, metadata: Dict[str, Any]) -> Dict[str, str]:
        """
        Registra un hash en blockchain externo
        Retorna transaction_id y block_number

        NOTA: Implementación futura con Web3.py o Hyperledger SDK
        """
        # Por ahora retorna datos simulados
        return {
            "transaction_id": f"0x{'0'*64}",
            "block_number": "0",
            "network": self.network,
            "status": "pending"
        }

    async def verify_transaction(self, transaction_id: str) -> bool:
        """
        Verifica una transacción en blockchain externo

        NOTA: Implementación futura
        """
        return True

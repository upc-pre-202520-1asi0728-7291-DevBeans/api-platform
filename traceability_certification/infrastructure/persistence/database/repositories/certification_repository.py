# traceability_certification/infrastructure/persistence/database/repositories/certification_repository.py

from typing import Optional

from sqlalchemy.orm import Session

from traceability_certification.domain.model.aggregates.certification_record import CertificationRecord


class CertificationRepository:
    """
    Repositorio para persistencia del agregado CertificationRecord
    """

    def __init__(self, db: Session):
        self.db = db

    def save(self, certification: CertificationRecord) -> CertificationRecord:
        """Guarda o actualiza un certificado"""
        self.db.add(certification)
        self.db.commit()
        self.db.refresh(certification)
        return certification

    def find_by_id(self, certification_id: int) -> Optional[CertificationRecord]:
        """Busca certificado por ID numérico"""
        return self.db.query(CertificationRecord).filter(
            CertificationRecord.id == certification_id
        ).first()

    def find_by_certification_id(self, certification_id: str) -> Optional[CertificationRecord]:
        """Busca certificado por ID legible (CERT-...)"""
        return self.db.query(CertificationRecord).filter(
            CertificationRecord.certification_id == certification_id
        ).first()

    def find_by_hash(self, certification_hash: str) -> Optional[CertificationRecord]:
        """Busca certificado por hash inmutable"""
        return self.db.query(CertificationRecord).filter(
            CertificationRecord.certification_hash == certification_hash
        ).first()

    def find_by_verification_token(self, token: str) -> Optional[CertificationRecord]:
        """Busca certificado por token de verificación pública"""
        return self.db.query(CertificationRecord).filter(
            CertificationRecord.verification_token == token
        ).first()

    def find_by_classification_session(self, session_id: int) -> Optional[CertificationRecord]:
        """Busca certificado por sesión de clasificación"""
        return self.db.query(CertificationRecord).filter(
            CertificationRecord.classification_session_id == session_id
        ).first()

    def find_by_coffee_lot(self, coffee_lot_id: int) -> list[type[CertificationRecord]]:
        """Obtiene todos los certificados de un lote de café"""
        return self.db.query(CertificationRecord).filter(
            CertificationRecord.coffee_lot_id == coffee_lot_id
        ).order_by(CertificationRecord.certified_at.desc()).all()

    def find_public_certifications(self) -> list[type[CertificationRecord]]:
        """Obtiene todos los certificados públicos"""
        return self.db.query(CertificationRecord).filter(
            CertificationRecord.is_public == True
        ).order_by(CertificationRecord.certified_at.desc()).all()

    def exists_by_hash(self, certification_hash: str) -> bool:
        """Verifica si existe un certificado con el hash dado"""
        return self.db.query(CertificationRecord).filter(
            CertificationRecord.certification_hash == certification_hash
        ).first() is not None

    def count_by_coffee_lot(self, coffee_lot_id: int) -> int:
        """Cuenta certificados de un lote"""
        return self.db.query(CertificationRecord).filter(
            CertificationRecord.coffee_lot_id == coffee_lot_id
        ).count()
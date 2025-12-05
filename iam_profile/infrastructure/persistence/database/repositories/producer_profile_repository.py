from iam_profile.domain.model.entities.producer_profile import ProducerProfile
from sqlalchemy.orm import Session
from typing import Optional


class ProducerProfileRepository:
    """Repositorio para ProducerProfile"""

    def __init__(self, db: Session):
        self.db = db

    def save(self, profile: ProducerProfile) -> ProducerProfile:
        """Guarda o actualiza un perfil de productor"""
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def find_by_user_id(self, user_id: int) -> Optional[ProducerProfile]:
        """Busca perfil por user_id"""
        return self.db.query(ProducerProfile).filter(ProducerProfile.user_id == user_id).first()

    def find_by_id(self, profile_id: int) -> Optional[ProducerProfile]:
        """Busca perfil por ID"""
        return self.db.query(ProducerProfile).filter(ProducerProfile.id == profile_id).first()

    def find_all(self) -> list[type[ProducerProfile]]:
        """Obtiene todos los perfiles de productores"""
        return self.db.query(ProducerProfile).all()
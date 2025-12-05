from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status


from iam_profile.domain.model.entities.producer_profile import ProducerProfile
from iam_profile.domain.model.entities.cooperative_profile import CooperativeProfile
from iam_profile.domain.model.queries.get_producer_profile_query import GetProducerProfileQuery
from iam_profile.domain.model.queries.get_cooperative_profile_query import GetCooperativeProfileQuery
from iam_profile.domain.model.queries.get_all_producers_query import GetAllProducersQuery
from iam_profile.infrastructure.persistence.database.repositories.producer_profile_repository import \
    ProducerProfileRepository
from iam_profile.infrastructure.persistence.database.repositories.cooperative_profile_repository import \
    CooperativeProfileRepository



class ProfileQueryService:
    """Servicio de queries para perfiles"""

    def __init__(self, db: Session):
        self.db = db
        self.producer_repository = ProducerProfileRepository(db)
        self.cooperative_repository = CooperativeProfileRepository(db)

    def handle_get_producer_profile(self, query: GetProducerProfileQuery) -> Optional[ProducerProfile]:
        """Obtiene perfil completo de productor"""
        profile = self.producer_repository.find_by_user_id(query.user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producer profile not found"
            )
        return profile

    def handle_get_cooperative_profile(self, query: GetCooperativeProfileQuery) -> Optional[CooperativeProfile]:
        """Obtiene perfil completo de cooperativa"""
        profile = self.cooperative_repository.find_by_user_id(query.user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cooperative profile not found"
            )
        return profile

    def handle_get_all_producers(self, query: GetAllProducersQuery) -> list[type[ProducerProfile]]:
        """Obtiene todos los perfiles de productores"""
        return self.producer_repository.find_all()
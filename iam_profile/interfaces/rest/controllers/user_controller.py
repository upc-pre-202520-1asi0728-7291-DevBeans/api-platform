from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from iam_profile.application.internal.commandservices.user_command_service import UserCommandService
from iam_profile.application.internal.queryservices.profile_query_service import ProfileQueryService
from iam_profile.domain.model.commands.change_password_command import ChangePasswordCommand
from iam_profile.domain.model.commands.update_profile_command import UpdateProfileCommand
from iam_profile.domain.model.queries.get_all_producers_query import GetAllProducersQuery
from iam_profile.interfaces.rest.resources.change_password_resource import ChangePasswordResource
from iam_profile.interfaces.rest.resources.producer_profile_resource import ProducerProfileResource
from iam_profile.interfaces.rest.resources.update_profile_resource import UpdateProfileResource
from iam_profile.interfaces.rest.resources.user_resource import UserResource
from shared.domain.database import get_db

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/producers", response_model=List[ProducerProfileResource])
async def get_all_producers(
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los productores registrados (para cooperativas)
    """
    profile_query_service = ProfileQueryService(db)
    query = GetAllProducersQuery()
    producers = profile_query_service.handle_get_all_producers(query)
    return [ProducerProfileResource.model_validate(p) for p in producers]


@router.put("/{user_id}/profile", response_model=UserResource)
async def update_profile(
    user_id: int,
    resource: UpdateProfileResource,
    db: Session = Depends(get_db)
):
    """
    Actualiza el perfil de un usuario
    """
    command = UpdateProfileCommand(
        user_id=user_id,
        **resource.model_dump(exclude_unset=True)
    )
    command_service = UserCommandService(db)
    user = command_service.handle_update_profile(command)
    return UserResource.model_validate(user)


@router.put("/{user_id}/password", response_model=UserResource)
async def change_password(
    user_id: int,
    resource: ChangePasswordResource,
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña de un usuario
    """
    command = ChangePasswordCommand(
        user_id=user_id,
        current_password=resource.current_password,
        new_password=resource.new_password
    )
    command_service = UserCommandService(db)
    user = command_service.handle_change_password(command)
    return UserResource.model_validate(user)
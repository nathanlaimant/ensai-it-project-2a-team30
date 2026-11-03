"""Gère les requêtes des administrateurs."""

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.authentication import get_current_admin
from dependencies.service import get_user_service
from schema.common_model import MessageResponse
from schema.user_model import UserResponse
from service.user_service import UserService
from utils.log_utils import get_logger
from utils.token_cache import app_token_cache

router = APIRouter(prefix="/admin", tags=["Administration"])

logger = get_logger(__name__)


@router.post("/users", response_model=list[UserResponse])
async def list_users(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
    admin_id: int = Depends(get_current_admin),
) -> list[UserResponse]:
    """
    Liste les utilisateurs selon des critères de recherche.

    Parameters
    ----------
    payload : dict
        Critères de filtrage et/ou de pagination.
    user_service : UserService
        Service pour gérer les utilisateurs.
    admin_id : int
        Identifiant de l'administrateur effectuant la requête.

    Returns
    -------
    list of User
        Liste des utilisateurs correspondant aux critères.
    """
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User search criteria must be an object.",
        )

    allowed_fields = {
        "user_id": int,
        "username": str,
        "email": str,
        "role": str,
        "is_active": bool,
        "limit": int,
        "offset": int,
    }
    if not set(payload).issubset(allowed_fields):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported user search criteria.",
        )

    for field, value in payload.items():
        expected_type = allowed_fields[field]
        if expected_type is int:
            is_valid_type = isinstance(value, int) and not isinstance(value, bool)
        else:
            is_valid_type = isinstance(value, expected_type)

        if not is_valid_type:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} has an invalid type.",
            )
        if field == "role" and value not in {"ADMIN", "USER"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="role must be ADMIN or USER.",
            )
        if field == "limit" and value <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="limit must be greater than zero.",
            )
        if field == "offset" and value < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="offset must not be negative.",
            )

    logger.info("Admin %s listed users with filters %s", admin_id, payload)
    users = user_service.list_users(payload)
    return [UserResponse.model_validate(user) for user in users]


@router.post("/users/activate/{user_id}", response_model=MessageResponse)
def activate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin_id: int = Depends(get_current_admin),
) -> MessageResponse:
    """
    Active le compte d'un utilisateur.

    Parameters
    ----------
    user_id : int
        Identifiant de l'utilisateur concerné.
    user_service : UserService
        Service pour gérer les utilisateurs.
    admin_id : int
        Identifiant de l'administrateur effectuant la requête.

    Returns
    -------
    str
        Message de confirmation de la mise à jour du statut.
    """
    users = user_service.list_users({"user_id": user_id, "limit": 1})
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if not user_service.update_user(user_id, {"is_active": True}):
        logger.error("Admin %s could not activate user %s", admin_id, user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to activate the user account.",
        )

    logger.info("Admin %s activated user %s", admin_id, user_id)
    return MessageResponse(message="User account activated successfully.")


@router.post("/users/deactivate/{user_id}", response_model=MessageResponse)
def deactivate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin_id: int = Depends(get_current_admin),
) -> MessageResponse:
    """
    Désactive le compte d'un utilisateur.

    Parameters
    ----------
    user_id : int
        Identifiant de l'utilisateur concerné.
    user_service : UserService
        Service pour gérer les utilisateurs.
    admin_id : int
        Identifiant de l'administrateur effectuant la requête.

    Returns
    -------
    str
        Message de confirmation de la mise à jour du statut.
    """
    users = user_service.list_users({"user_id": user_id, "limit": 1})
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user = users[0]
    if not user_service.update_user(
        user_id,
        {"is_active": False, "access_token": None},
    ):
        logger.error("Admin %s could not deactivate user %s", admin_id, user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to deactivate the user account.",
        )

    if user.access_token:
        app_token_cache.delete(user.access_token)

    logger.info("Admin %s deactivated user %s", admin_id, user_id)
    return MessageResponse(message="User account deactivated successfully.")

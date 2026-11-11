"""Gère les requêtes des administrateurs."""

from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore[import-not-found]

from dependencies.authentication import get_current_admin
from dependencies.service import get_user_service
from schema.common_model import MessageResponse
from schema.user_model import UserResponse, UserSearchRequest
from service.user_service import UserService
from utils.log_utils import get_logger
from utils.token_cache import app_token_cache

router = APIRouter(prefix="/admin", tags=["Administration"])

logger = get_logger(__name__)


@router.post("/users", response_model=list[UserResponse])
async def list_users(
    payload: UserSearchRequest,
    user_service: UserService = Depends(get_user_service),
    admin_id: int = Depends(get_current_admin),
) -> list[UserResponse]:
    """
    Liste les utilisateurs selon des critères de recherche.
    **Authentification requise** : Fournir l'header `Authorization: Bearer <access_token>`.

    Parameters
    ----------
    payload : UserSearchRequest
        Critères de filtrage et/ou de pagination.
    user_service : UserService
        Service pour gérer les utilisateurs.
    admin_id : int
        Identifiant de l'administrateur effectuant la requête.

    Returns
    -------
    list[UserResponse]
        Liste des utilisateurs correspondant aux critères.
    """
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
    **Authentification requise** : Fournir l'header `Authorization: Bearer <access_token>`.

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
    MessageResponse
        Message de confirmation de la mise à jour du statut.
    """
    if user_id == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to activate yourself.",
        )

    user = user_service.get_user_by_id(user_id)
    if user is None:
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
    **Authentification requise** : Fournir l'header `Authorization: Bearer <access_token>`.

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
    MessageResponse
        Message de confirmation de la mise à jour du statut.
    """
    if user_id == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to deactivate yourself.",
        )

    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

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


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin_id: int = Depends(get_current_admin),
) -> MessageResponse:
    """Supprime définitivement le compte d'un utilisateur."""
    if user_id == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account.",
        )

    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if not user_service.delete_user(user_id):
        logger.error("Admin %s could not delete user %s", admin_id, user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the user account.",
        )

    if user.access_token:
        app_token_cache.delete(user.access_token)

    logger.info("Admin %s deleted user %s", admin_id, user_id)
    return MessageResponse(message="User account deleted successfully.")

"""Gère les requêtes des administrateurs."""

from fastapi import APIRouter, Depends, HTTPException

from business_object.user import User
from dependencies import get_current_user, get_user_service
from service.user_service import UserService
from utils.log_utils import get_logger

router = APIRouter(prefix="/admin", tags=["Administration"])

logger = get_logger(__name__)


@router.get("/users")
async def list_users(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
    admin_id: int = Depends(get_current_user),
) -> list[User]:
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
    raise NotImplementedError


@router.post("/users/activate/{user_id}")
def activate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin_id: int = Depends(get_current_user),
) -> str:
    """Active le compte d'un utilisateur.

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
        Message de confirmation de la mise à jour du statut."""
    raise NotImplementedError


@router.post("/users/deactivate/{user_id}")
def deactivate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin_id: int = Depends(get_current_user),
) -> str:
    """Désactive le compte d'un utilisateur.

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
        Message de confirmation de la mise à jour du statut."""
    raise NotImplementedError

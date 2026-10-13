"""Gère les requètes d'authentification et de modifications de comptes utilisateurs."""

from fastapi import APIRouter, Depends, HTTPException

from dependencies.authentication import get_current_user
from dependencies.service import get_user_service
from schema.common_model import MessageResponse
from schema.user_model import LoginResponse, UserResponse
from service.user_service import UserService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


@router.post("/signup", response_model=MessageResponse, tags=["Authentication"])
async def signup(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
) -> MessageResponse:
    """
    Inscrit un nouvel utilisateur.

    Parameters
    ----------
    payload : dict
        Données d'inscription (ex: username, email, mot de passe).

    Returns
    -------
    str
        Message de confirmation ou identifiant de l'utilisateur créé.
    """
    raise NotImplementedError


@router.post("/login", response_model=LoginResponse, tags=["Authentication"])
async def login(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
) -> LoginResponse:
    """
    Authentifie un utilisateur et retourne ses informations de session.

    Parameters
    ----------
    payload : dict
        Identifiants de connexion (ex: username, mot de passe).

    Returns
    -------
    dict
        Informations de session (ex: jeton d'accès, données utilisateur).
    """
    raise NotImplementedError


@router.post("/logout", response_model=MessageResponse, tags=["Authentication"])
async def logout(
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> MessageResponse:
    """
    Déconnecte l'utilisateur actuellement authentifié.

    Returns
    -------
    str
        Message de confirmation de déconnexion.
    """
    raise NotImplementedError


@router.get("/user/info", response_model=UserResponse, tags=["Users"])
async def get_user_info(
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> UserResponse:
    """
    Récupère les informations du profil de l'utilisateur courant.

    Returns
    -------
    User
        Instance représentant l'utilisateur authentifié.
    """
    raise NotImplementedError


@router.put("/user/info", response_model=MessageResponse, tags=["Users"])
async def update_user_info(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> MessageResponse:
    """
    Met à jour les informations du profil de l'utilisateur courant.

    Parameters
    ----------
    payload : dict
        Champs du profil à mettre à jour.

    Returns
    -------
    str
        Message de confirmation de la mise à jour.
    """
    raise NotImplementedError

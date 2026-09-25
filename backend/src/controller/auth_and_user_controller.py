"""Gère les requètes d'authentification et de modifications de comptes utilisateurs."""

from fastapi import APIRouter, Depends, HTTPException

from business_object.user import User
from dependencies import get_current_user, get_user_service
from service.user_service import UserService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)

@router.post("/signup", tags=["Authentication"])
async def signup(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
) -> str:
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


@router.post("/login", tags=["Authentication"])
async def login(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
) -> dict:
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


@router.post("/logout", tags=["Authentication"])
async def logout(
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> str:
    """
    Déconnecte l'utilisateur actuellement authentifié.
 
    Returns
    -------
    str
        Message de confirmation de déconnexion.
    """
    raise NotImplementedError


@router.get("/user/info", tags=["Users"])
async def get_user_info(
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> User:
    """
    Récupère les informations du profil de l'utilisateur courant.
 
    Returns
    -------
    User
        Instance représentant l'utilisateur authentifié.
    """
    raise NotImplementedError


@router.put("/user/info", tags=["Users"])
async def update_user_info(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> str:
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

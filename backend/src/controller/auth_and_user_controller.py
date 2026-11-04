"""Gère les requètes d'authentification et de modifications de comptes utilisateurs."""

import psycopg2
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.authentication import get_current_user
from dependencies.service import get_user_service
from schema.common_model import MessageResponse
from schema.user_model import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    UserResponse,
    UserUpdateRequest,
)
from service.user_service import UserService
from utils.log_utils import get_logger
from utils.security import hash_password

router = APIRouter()

logger = get_logger(__name__)


@router.post("/signup", response_model=MessageResponse, tags=["Authentication"])
async def signup(
    payload: SignupRequest,
    user_service: UserService = Depends(get_user_service),
) -> MessageResponse:
    """
    Inscrit un nouvel utilisateur.

    Parameters
    ----------
    payload : SignupRequest
        Données d'inscription (ex: username, email, mot de passe).

    Returns
    -------
    MessageResponse
        Message de confirmation ou identifiant de l'utilisateur créé.
    """
    signed_up = False
    try:
        signed_up = user_service.signup(payload.model_dump())
    except psycopg2.IntegrityError:
        signed_up = False
    if not signed_up:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create the account. Username or email may already exist.",
        )

    logger.info("New user signup requested for username %s", payload.username)
    return MessageResponse(message="Account created successfully.")


@router.get("/login", response_model=LoginResponse, tags=["Authentication"])
async def login(
    payload: LoginRequest,
    user_service: UserService = Depends(get_user_service),
) -> LoginResponse:
    """
    Authentifie un utilisateur et retourne ses informations de session.

    Parameters
    ----------
    payload : LoginRequest
        Identifiants de connexion (ex: username, mot de passe).

    Returns
    -------
    LoginResponse
        Informations de session (ex: jeton d'accès, données utilisateur).
    """
    username = payload.username.strip()
    password = payload.password
    login_response = user_service.login(username, hash_password(password))
    if login_response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )
    return login_response


@router.post("/logout", response_model=MessageResponse, tags=["Authentication"])
async def logout(
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> MessageResponse:
    """
    Déconnecte l'utilisateur actuellement authentifié.
    **Authentification requise** : Fournir l'header `Authorization: Bearer <access_token>`.

    Returns
    -------
    MessageResponse
        Message de confirmation de déconnexion.
    """
    if not user_service.logout(user_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to invalidate the current session.",
        )
    return MessageResponse(message="Logged out successfully.")


@router.get("/user/info", response_model=UserResponse, tags=["Users"])
async def get_user_info(
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> UserResponse:
    """
    Récupère les informations du profil de l'utilisateur courant.
    **Authentification requise** : Fournir l'header `Authorization: Bearer <access_token>`.

    Returns
    -------
    UserResponse
        Instance représentant l'utilisateur authentifié.
    """
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )
    return UserResponse.model_validate(user)


@router.put("/user/info", response_model=MessageResponse, tags=["Users"])
async def update_user_info(
    payload: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> MessageResponse:
    """
    Met à jour les informations du profil de l'utilisateur courant.
    **Authentification requise** : Fournir l'header `Authorization: Bearer <access_token>`.

    Parameters
    ----------
    payload : UserUpdateRequest
        Champs du profil à mettre à jour.

    Returns
    -------
    MessageResponse
        Message de confirmation de la mise à jour.
    """
    updates = {}
    if payload.username:
        updates["username"] = payload.username.strip()
    if payload.email:
        updates["email"] = payload.email.strip()
    if payload.password:
        updates["password_hashed"] = hash_password(payload.password)
    updated = False
    try:
        updated = user_service.update_user(user_id, updates)
    except psycopg2.IntegrityError:
        updated = False
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update the profile. Username or email may already exist.",
        )
    return MessageResponse(message="Profile updated successfully.")

"""Gère les requètes d'authentification et de modifications de comptes utilisateurs."""

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.authentication import get_current_user
from dependencies.service import get_user_service
from schema.common_model import MessageResponse
from schema.user_model import LoginRequest, LoginResponse, SignupRequest, UserResponse
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
    if not user_service.signup(payload.model_dump()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create the account. Username or email may already exist.",
        )

    logger.info("New user signup requested for username %s", payload.username)
    return MessageResponse(message="Account created successfully.")


@router.post("/login", response_model=LoginResponse, tags=["Authentication"])
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
    users = user_service.list_users({"user_id": user_id, "limit": 1})
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )
    return UserResponse.model_validate(users[0])


@router.put("/user/info", response_model=MessageResponse, tags=["Users"])
async def update_user_info(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> MessageResponse:
    """
    Met à jour les informations du profil de l'utilisateur courant.
    **Authentification requise** : Fournir l'header `Authorization: Bearer <access_token>`.

    Parameters
    ----------
    payload : dict
        Champs du profil à mettre à jour.

    Returns
    -------
    str
        Message de confirmation de la mise à jour.
    """
    if not isinstance(payload, dict) or not payload:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one profile field must be provided.",
        )

    allowed_fields = {"username", "email", "password"}
    if not set(payload).issubset(allowed_fields):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only username, email and password can be updated.",
        )

    updates = {}
    for field, value in payload.items():
        if not isinstance(value, str) or not value.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} must be a non-empty string.",
            )
        if field == "password":
            updates["password_hashed"] = hash_password(value)
        else:
            updates[field] = value.strip()

    if not user_service.update_user(user_id, updates):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update the profile. Username or email may already exist.",
        )
    return MessageResponse(message="Profile updated successfully.")

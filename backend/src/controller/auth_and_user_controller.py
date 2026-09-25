"""Handle authentication and user requests."""

from fastapi import APIRouter, Depends, HTTPException

from business_object.user import User
from dependencies import get_current_user, get_user_service
from service.user_service import UserService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


class AuthAndUserController:
    """
    Gère les requètes d'authentification et de modifications de comptes utilisateurs.
    
    Parameters
    ----------
    user_service : Any
        Service applicatif gérant la logique métier liée
        aux comptes des utilisateurs (inscription, connexion, mise à jour du profil).
    """


@router.post("/login", tags=["Authentication"])
async def login(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
) -> dict:
    """Log in a user."""
    raise NotImplementedError


@router.post("/logout", tags=["Authentication"])
async def logout(
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> str:
    """Log out the current user."""
    raise NotImplementedError


@router.get("/user/info", tags=["Users"])
async def get_user_info(
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> User:
    """Get the current user's information."""
    raise NotImplementedError


@router.put("/user/info", tags=["Users"])
async def update_user_info(
    payload: dict,
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user),
) -> str:
    """Update the current user's information."""
    raise NotImplementedError

"""Handle administration requests."""

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
    """List users."""
    raise NotImplementedError


@router.post("/users/activate/{user_id}")
def activate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin_id: int = Depends(get_current_user),
) -> str:
    """Activate an user."""
    raise NotImplementedError


@router.post("/users/deactivate/{user_id}")
def deactivate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin_id: int = Depends(get_current_user),
) -> str:
    """Deactivate an user."""
    raise NotImplementedError

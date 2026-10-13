"""Dependency providers for application services."""

from fastapi import Depends

from dao.user_dao import UserDAO
from dependencies.dao import get_user_dao
from service.user_service import UserService


def get_user_service(
    user_dao: UserDAO = Depends(get_user_dao),
) -> UserService:
    """Construit une instance de UserService."""
    return UserService(user_dao)

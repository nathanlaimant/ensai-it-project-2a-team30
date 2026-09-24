from ..business_object import User
from ..service import UserService


class AdminController:
    """Handle administration requests."""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def list_users(self, payload: dict) -> list[User]:
        """List users."""
        raise NotImplementedError

    def update_user_status(self, user_id: int, is_active: bool) -> str:
        """Update a user's active status."""
        raise NotImplementedError

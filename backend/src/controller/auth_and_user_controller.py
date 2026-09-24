from ..business_object import User
from ..service import UserService


class AuthAndUserController:
    """Handle authentication and user requests."""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def signup(self, payload: dict) -> str:
        """Sign up a user."""
        raise NotImplementedError

    def login(self, payload: dict) -> dict:
        """Log in a user."""
        raise NotImplementedError

    def logout(self) -> str:
        """Log out the current user."""
        raise NotImplementedError

    def get_user_info(self) -> User:
        """Get the current user's information."""
        raise NotImplementedError

    def update_user_info(self, payload: dict) -> str:
        """Update the current user's information."""
        raise NotImplementedError

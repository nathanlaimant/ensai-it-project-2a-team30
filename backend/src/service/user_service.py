from ..business_object import User
from ..dao import UserDAO


class UserService:
    """Coordinate user operations."""

    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    def signup(self, dto: dict) -> bool:
        """Register a user."""
        raise NotImplementedError

    def login(self, username: str, password_hashed: str) -> str:
        """Authenticate a user."""
        raise NotImplementedError

    def logout(self, user_id: int) -> bool:
        """End a user's session."""
        raise NotImplementedError

    def list_users(self, query_params: dict) -> list[User]:
        """List users."""
        raise NotImplementedError

    def update_user(self, user_id: int, updates: dict) -> bool:
        """Update user information."""
        raise NotImplementedError

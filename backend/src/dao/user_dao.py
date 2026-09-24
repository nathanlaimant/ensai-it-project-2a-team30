from ..business_object import User


class UserDAO:
    """Access users in persistent storage."""

    def create_user(self, user: User) -> bool:
        """Create a user."""
        raise NotImplementedError

    def get_by_id(self, user_id: int) -> User:
        """Find a user by identifier."""
        raise NotImplementedError

    def get_by_username(self, username: str) -> User:
        """Find a user by username."""
        raise NotImplementedError

    def get_by_access_token(self, token: str) -> User:
        """Find a user by access token."""
        raise NotImplementedError

    def list_users(self, query_params: dict) -> list[User]:
        """List users matching query parameters."""
        raise NotImplementedError

    def update_user(self, user_id: int, updates: dict) -> bool:
        """Update a user."""
        raise NotImplementedError

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        raise NotImplementedError

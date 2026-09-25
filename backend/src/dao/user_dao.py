from business_object.user import User
from utils.db_connection import DbConnection


class UserDAO:
    """Access users in persistent storage."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def create_user(self, user: User) -> bool:
        """Create a user."""
        raise NotImplementedError

    def get_by_id(self, user_id: int) -> User | None:
        """Find a user by identifier."""
        player = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM users WHERE id = %(user_id)s",
                        {"user_id": user_id},
                    )
                    result = cursor.fetchone()
                    if result:
                        player = User(**result)
        except Exception as e:
            raise
        return player

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

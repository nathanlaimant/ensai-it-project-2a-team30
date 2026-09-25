from threading import Lock


class InMemTokenCache:
    """A simple in-memory cache for storing tokens."""

    def __init__(self) -> None:
        self.__cache: dict[str, int] = {}
        self.__lock = Lock()

    def set(self, token: str, user_id: int) -> None:
        """Set a token in the cache with the associated user ID.

        Parameters
        ----------
        token : str
            The token to be stored in the cache.
        user_id : int
            The user ID associated with the token.
        """
        with self.__lock:
            self.__cache[token] = user_id

    def get(self, token: str) -> int | None:
        """Get the associated user ID for a given token from the cache.

        Parameters
        ----------
        token : str
            The token for which the associated user ID is to be retrieved.

        Returns
        -------
        int | None
            The associated user ID if the token exists in the cache, otherwise None.
        """
        with self.__lock:
            return self.__cache.get(token)

    def delete(self, token: str) -> None:
        """Delete a token from the cache.

        Parameters
        ----------
        token : str
            The token to be deleted from the cache.
        """
        with self.__lock:
            self.__cache.pop(token, None)


app_token_cache = InMemTokenCache()

from threading import Lock


class InMemTokenCache:
    """Cache en mémoire simple pour stocker des jetons d'authentification."""

    def __init__(self) -> None:
        self.__cache: dict[str, tuple[int, str]] = {}
        self.__lock = Lock()

    def set(self, token: str, user_and_role: tuple[int, str]) -> None:
        """
        Enregistre un jeton dans le cache, associé à un identifiant utilisateur.

        Parameters
        ----------
        token : str
            Jeton à stocker dans le cache.
        user_and_role : tuple[int, str]
            Tuple contenant l'identifiant de l'utilisateur et son rôle.

        Returns
        -------
        None
        """
        with self.__lock:
            self.__cache[token] = user_and_role

    def get(self, token: str) -> tuple[int, str] | None:
        """
        Récupère l'identifiant utilisateur associé à un jeton donné.

        Parameters
        ----------
        token : str
            Jeton dont on souhaite récupérer l'identifiant utilisateur associé.

        Returns
        -------
        tuple[int, str] | None
            Le tuple contenant l'identifiant utilisateur et son rôle si le jeton existe dans le cache, sinon None.
        """
        with self.__lock:
            return self.__cache.get(token)

    def delete(self, token: str) -> None:
        """
        Supprime un jeton du cache.

        Parameters
        ----------
        token : str
            Jeton à supprimer du cache.

        Returns
        -------
        None
        """
        with self.__lock:
            self.__cache.pop(token, None)


app_token_cache = InMemTokenCache()

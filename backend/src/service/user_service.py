from datetime import datetime, timezone

from business_object.user import User
from dao.user_dao import UserDAO
from utils.security import generate_user_token, hash_password
from utils.token_cache import app_token_cache


class UserService:
    """
    Gère la logique métier liée aux utilisateurs.

    Parameters
    ----------
    user_dao : UserDAO
        DAO permettant l'accès aux données des utilisateurs.
    """

    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    def signup(self, dto: dict) -> bool:
        """
        Inscrit un nouvel utilisateur.

        Parameters
        ----------
        dto : dict
            Données d'inscription (ex: username, email, mot de passe).

        Returns
        -------
        bool
            True si l'inscription a réussi.
        """
        if not isinstance(dto, dict):
            return False

        username = dto.get("username")
        email = dto.get("email")
        password = dto.get("password")
        if not all(isinstance(value, str) and value.strip() for value in (username, email, password)):
            return False

        now = datetime.now(timezone.utc)
        user = User(
            username=username.strip(),
            password_hashed=hash_password(password),
            email=email.strip(),
            role="USER",
            is_active=True,
            created_at=now,
            updated_at=now,
            access_token="",
        )
        return self.user_dao.create_user(user)

    def login(self, username: str, password_hashed: str) -> str | None:
        """
        Authentifie un utilisateur à partir de ses identifiants.

        Parameters
        ----------
        username : str
            Nom d'utilisateur.
        password_hashed : str
            Mot de passe haché de l'utilisateur.

        Returns
        -------
        str
            Jeton d'accès de la session créée.
            Ne renvoie rien si les deux arguments ne correspondent pas au nom d'utilisateur
            et au mot de passe d'un même utilisateur.
        """
        if not isinstance(username, str) or not isinstance(password_hashed, str):
            return None

        user = self.user_dao.get_by_username(username)
        if (
            user is None
            or not user.is_active
            or user.password_hashed != password_hashed
            or user.user_id is None
        ):
            return None

        access_token = generate_user_token()
        if not self.user_dao.update_user(user.user_id, {"access_token": access_token}):
            return None

        app_token_cache.set(access_token, (user.user_id, user.role))
        return access_token

    def logout(self, user_id: int) -> bool:
        """
        Déconnecte un utilisateur en invalidant sa session courante.

        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur à déconnecter.

        Returns
        -------
        bool
            True si la déconnexion a réussi.
        """
        if isinstance(user_id, bool) or not isinstance(user_id, int):
            return False

        user = self.user_dao.get_by_id(user_id)
        if user is None:
            return False

        if not self.user_dao.update_user(user_id, {"access_token": None}):
            return False

        if user.access_token:
            app_token_cache.delete(user.access_token)
        return True

    def list_users(self, query_params: dict) -> list[User]:
        """
        Liste les utilisateurs selon des critères de recherche.

        Parameters
        ----------
        query_params : dict
            Critères de filtrage et/ou de pagination.

        Returns
        -------
        list of User
            Liste des utilisateurs correspondant aux critères.
            Ne renvoie rien si l'un des critères n'est pas dans le bon format.
        """
        return self.user_dao.list_users(query_params)

    def update_user(self, user_id: int, updates: dict) -> bool:
        """
        Met à jour les informations d'un utilisateur.

        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur à mettre à jour.
        updates : dict
            Champs à mettre à jour.

        Returns
        -------
        bool
            True si la mise à jour a réussi.
        """
        return self.user_dao.update_user(user_id, updates)

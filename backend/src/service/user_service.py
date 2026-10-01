from ..business_object import User
from ..dao import UserDAO


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
        raise NotImplementedError

    def login(self, username: str, password_hashed: str) -> str:
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
        """
        raise NotImplementedError

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
        raise NotImplementedError

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
        """
        raise NotImplementedError

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
        raise NotImplementedError

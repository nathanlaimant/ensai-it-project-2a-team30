from business_object.user import User
from utils.db_connection import DbConnection


class UserDAO:
    """Gère l'accès aux données des utilisateurs en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def create_user(self, user: User) -> bool:
        """
        Crée un nouvel utilisateur en base de données.
 
        Parameters
        ----------
        user : User
            Instance de l'utilisateur à créer.
 
        Returns
        -------
        bool
            True si la création a réussi.
        """
        raise NotImplementedError

    def get_by_id(self, user_id: int) -> User | None:
        """
        Récupère un utilisateur à partir de son identifiant.
 
        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur recherché.
 
        Returns
        -------
        User
            Instance de l'utilisateur correspondant, ou None si introuvable.
        """
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
        """
        Récupère un utilisateur à partir de son nom d'utilisateur.
 
        Parameters
        ----------
        username : str
            Nom d'utilisateur recherché.
 
        Returns
        -------
        User
            Instance de l'utilisateur correspondant, ou None si introuvable.
        """
        raise NotImplementedError

    def get_by_access_token(self, token: str) -> User:
        """
        Récupère un utilisateur à partir de son jeton d'accès.
 
        Parameters
        ----------
        token : str
            Jeton d'accès de l'utilisateur.
 
        Returns
        -------
        User
            Instance de l'utilisateur correspondant, ou None si introuvable.
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

    def delete_user(self, user_id: int) -> bool:
        """
        Supprime un utilisateur de la base de données.
 
        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur à supprimer.
 
        Returns
        -------
        bool
            True si la suppression a réussi.
        """
        raise NotImplementedError

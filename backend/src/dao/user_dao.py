from business_object.user import User
from utils.db_connection import DBConnection
import psycopg2


class UserDAO:
    """Gère l'accès aux données des utilisateurs en base de données."""

    filtres_autorises = {
        "user_id": int,
        "username": str,
        "email": str,
        "role": str,
        "is_active": bool,
    }

    roles_valides = {"ADMIN", "USER"}

    champs_modifiables = {
        "username": str,
        "email": str,
        "password_hash": str,
        "role": str,
        "is_active": bool,
        "access_token": (str, type(None)),  # nullable
    }

    def _construire_update(self, user_id: int, updates: dict) -> tuple[str, dict]:
        """Construit la requête UPDATE et ses valeurs (paramètres déjà validés)."""
        affectations = [f"{cle} = %({cle})s" for cle in updates]
        affectations.append("updated_at = now()")

        requete = f'UPDATE "user" SET {", ".join(affectations)} WHERE user_id = %(user_id)s'

        valeurs = {**updates, "user_id": user_id}
        return requete, valeurs

    def _valider_update(self, user_id, updates) -> bool:
        """Vérifie que user_id et updates sont bien formés."""
        if not self._est_entier(user_id):
            return False

        if not isinstance(updates, dict) or not updates:
            return False

        for cle, valeur in updates.items():
            if cle not in self.champs_modifiables:
                return False

            if not isinstance(valeur, self.champs_modifiables[cle]):
                return False

            if cle in ("username", "email", "password_hash") and not valeur.strip():
                return False

            if cle == "role" and valeur not in self.roles_valides:
                return False

        return True

    @staticmethod
    def _est_entier(valeur) -> bool:
        """True si la valeur est un int mais pas un bool, False sinon"""
        return isinstance(valeur, int) and not isinstance(valeur, bool)

    def _valider(self, query_params: dict) -> bool:
        """Vérifie que les paramètres de la query sont bien valides"""
        if not isinstance(query_params, dict):
            return False

        for cle, valeur in query_params.items():
            if cle in self.filtres_autorises:
                type_attendu = self.filtres_autorises[cle]
                if type_attendu is int:
                    if not self._est_entier(valeur):
                        return False
                elif not isinstance(valeur, type_attendu):
                    return False
                if cle == "role" and valeur not in self.roles_valides:
                    return False
            elif cle == "limit":
                if not self._est_entier(valeur) or valeur <= 0:
                    return False
            elif cle == "offset":
                if not self._est_entier(valeur) or valeur < 0:
                    return False
            else:
                return False
        return True

    def _construire_requete(self, query_params: dict) -> tuple[str, dict]:
        """Construit la requête SQL et ses valeurs à partir de paramètres validés."""
        requete = (
            "SELECT user_id, username, password_hash, email, role, "
            "is_active, created_at, updated_at, access_token "
            'FROM "user"'
        )

        conditions = [f"{cle} = %({cle})s" for cle in query_params if cle in self.filtres_autorises]
        if conditions:
            requete += " WHERE " + " AND ".join(conditions)

        requete += " ORDER BY user_id"

        if "limit" in query_params:
            requete += " LIMIT %(limit)s"
        if "offset" in query_params:
            requete += " OFFSET %(offset)s"

        return requete, dict(query_params)

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
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO "user" (username, password_hash, email, role)
                    VALUES (%(username)s, %(password_hash)s, %(email)s, %(role)s)
                    RETURNING user_id;
                    """,
                    {
                        "username": user.username,
                        "password_hash": pwd,
                        "email": user.email,
                        "role": user.role,
                    },
                )
                res = cursor.fetchone()
                if res:
                    user.user_id = res["user_id"]
                    return True

        return False

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
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM "user" WHERE username = %(username)s;""",
                    {"username": username},
                )
                result = cursor.fetchone()
                if result:
                    return User(
                        user_id=result["user_id"],
                        username=result["username"],
                        password_hashed=result["password_hash"],
                        email=result["email"],
                        role=result["role"],
                        is_active=result["is_active"],
                        created_at=result["created_at"],
                        updated_at=result["updated_at"],
                        access_token=result["access_token"],
                    )

        return None

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
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM "user" WHERE access_token = %(token)s;""",
                    {"token": token},
                )
                result = cursor.fetchone()
                if result:
                    return User(
                        user_id=result["user_id"],
                        username=result["username"],
                        password_hashed=result["password_hash"],
                        email=result["email"],
                        role=result["role"],
                        is_active=result["is_active"],
                        created_at=result["created_at"],
                        updated_at=result["updated_at"],
                        access_token=result["access_token"],
                    )
        return None

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
            Ne renvoie rien si l'un des critères de recherche n'est pas dans le bon format.
        """
        if not self._valider(query_params):
            return []

        requete, valeurs = self._construire_requete(query_params)

        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(requete, valeurs)
                lignes = cursor.fetchall()

        return [
            User(
                user_id=ligne["user_id"],
                username=ligne["username"],
                password_hashed=ligne["password_hash"],
                email=ligne["email"],
                role=ligne["role"],
                is_active=ligne["is_active"],
                created_at=ligne["created_at"],
                updated_at=ligne["updated_at"],
                access_token=ligne["access_token"],
            )
            for ligne in lignes
        ]

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
        if not self._valider_update(user_id, updates):
            return False

        requete, valeurs = self._construire_update(user_id, updates)

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(requete, valeurs)
                    nb_lignes = cursor.rowcount
        except psycopg2.IntegrityError:
            return False

        return nb_lignes == 1

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
        if not self._est_entier(user_id):
            return False
        requete = 'DELETE FROM "user" WHERE user_id = %(user_id)s'

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(requete, {"user_id": user_id})
                    nb_lignes = cursor.rowcount
        except psycopg2.IntegrityError:
            return False

        return nb_lignes == 1

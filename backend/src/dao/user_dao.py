from typing import Any

import psycopg2

from business_object.user import User
from utils.db_connection import DbConnection


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

    champs_modifiables: dict[str, type | tuple[type, ...]] = {
        "username": str,
        "email": str,
        "password_hashed": str,
        "role": str,
        "is_active": bool,
        "access_token": (str, type(None)),  # nullable
    }

    def _construire_update(self, user_id: int, updates: dict) -> tuple[str, dict]:
        """Construit la requête UPDATE et ses valeurs (paramètres déjà validés)."""
        affectations = [f"{cle} = %({cle})s" for cle in updates]
        affectations.append("updated_at = now()")

        requete = (
            f'UPDATE "user" SET {", ".join(affectations)} WHERE user_id = %(user_id)s'
        )

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

            if cle in ("username", "email", "password_hashed") and not valeur.strip():
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
            "SELECT user_id, username, password_hashed, email, role, "
            "is_active, created_at, updated_at, access_token "
            'FROM "user"'
        )

        conditions = [
            f"{cle} = %({cle})s"
            for cle in query_params
            if cle in self.filtres_autorises
        ]
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
        with self._db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO "user" (username, password_hashed, email, role)
                    VALUES (%(username)s, %(password_hashed)s, %(email)s, %(role)s)
                    RETURNING user_id;
                    """,
                    {
                        "username": user.username,
                        "password_hashed": user.password_hashed,
                        "email": user.email,
                        "role": user.role,
                    },
                )
                res = cursor.fetchone()
                if res:
                    conn.commit()
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
        with self._db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'SELECT * FROM "user" WHERE user_id = %(user_id)s',
                    {"user_id": user_id},
                )
                result = cursor.fetchone()
                if result:
                    return User(**result)
        return None

    def get_by_username(self, username: str) -> User | None:
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
        with self._db_connection.get_connection() as conn:
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
                        password_hashed=result["password_hashed"],
                        email=result["email"],
                        role=result["role"],
                        is_active=result["is_active"],
                        created_at=result["created_at"],
                        updated_at=result["updated_at"],
                        access_token=result["access_token"],
                    )

        return None

    def get_by_access_token(self, token: str) -> User | None:
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
        with self._db_connection.get_connection() as conn:
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
                        password_hashed=result["password_hashed"],
                        email=result["email"],
                        role=result["role"],
                        is_active=result["is_active"],
                        created_at=result["created_at"],
                        updated_at=result["updated_at"],
                        access_token=result["access_token"],
                    )
        return None

    def list_users(
        self,
        user_id: int | dict | None = None,
        username: str | None = None,
        email: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        nb_pages: int | None = None,
    ) -> list[User]:
        """
        Liste les utilisateurs selon des critères de recherche.
        Tous les arguments de la méthode sont optionnels.

        Parameters
        ----------
        user_id : int | dict, optional
            Identifiant de l'utilisateur, ou dictionnaire de filtres complet.
        username : str, optional
            Nom d'utilisateur (recherche partielle insensible à la casse).
        email : str, optional
            Adresse e-mail (recherche partielle insensible à la casse).
        role : str, optional
            Rôle recherché ('ADMIN' ou 'USER').
        is_active : bool, optional
            Si True, liste les comptes actifs ; si False, les inactifs.
        limit : int, optional
            Nombre maximal d'utilisateurs à renvoyer.
        offset : int, optional
            Décalage pour la pagination.
        nb_pages : int, optional
            Nombre de pages pour découper la liste retournée.

        Returns
        -------
        list of User
            Liste des utilisateurs correspondant aux critères.
            Renvoie une liste vide si un critère n'est pas dans le bon format.
        """
        if isinstance(user_id, dict):
            params_dict = user_id
            user_id = params_dict.get("user_id")
            username = params_dict.get("username")
            email = params_dict.get("email")
            role = params_dict.get("role")
            is_active = params_dict.get("is_active")
            limit = params_dict.get("limit")
            offset = params_dict.get("offset")
            nb_pages = params_dict.get("nb_pages")

        if user_id is not None and (
            isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0
        ):
            return []
        if username is not None and not isinstance(username, str):
            return []
        if email is not None and not isinstance(email, str):
            return []
        if role is not None and (
            not isinstance(role, str) or role not in ("ADMIN", "USER")
        ):
            return []
        if is_active is not None and not isinstance(is_active, bool):
            return []
        if limit is not None and (
            isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0
        ):
            return []
        if offset is not None and (
            isinstance(offset, bool) or not isinstance(offset, int) or offset < 0
        ):
            return []
        if nb_pages is not None and (
            isinstance(nb_pages, bool) or not isinstance(nb_pages, int) or nb_pages <= 0
        ):
            return []

        conditions: list[str] = []
        params: dict[str, Any] = {}

        if user_id is not None:
            conditions.append("user_id = %(user_id)s")
            params["user_id"] = user_id

        if username is not None:
            conditions.append("username ILIKE %(username)s")
            params["username"] = f"%{username}%"

        if email is not None:
            conditions.append("email ILIKE %(email)s")
            params["email"] = f"%{email}%"

        if role is not None:
            conditions.append("role = %(role)s")
            params["role"] = role

        if is_active is not None:
            conditions.append("is_active = %(is_active)s")
            params["is_active"] = is_active

        query = """
            SELECT user_id, username, password_hashed, email, role, is_active
            FROM "user"
        """
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY user_id"

        if limit is not None:
            query += " LIMIT %(limit)s"
            params["limit"] = limit

        if offset is not None:
            query += " OFFSET %(offset)s"
            params["offset"] = offset

        # 4. Exécution de la requête avec gestion d'erreurs
        res = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    res = cursor.fetchall()
        except Exception as e:
            # Remplacer par votre logger si importé (ex: logger.error(e))
            print(f"Erreur SQL dans list_users : {e}")
            raise

        return [
            User(
                user_id=row["user_id"],
                username=row["username"],
                password_hashed=row["password_hashed"],
                email=row["email"],
                role=row["role"],
                is_active=row["is_active"],
            )
            for row in res or []
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
            with self._db_connection.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(requete, valeurs)
                    nb_lignes = cursor.rowcount
                    connection.commit()
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
            with self._db_connection.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(requete, {"user_id": user_id})
                    nb_lignes = cursor.rowcount
                    connection.commit()
        except psycopg2.IntegrityError:
            return False

        return nb_lignes == 1

from business_object.station_information import StationInformation
from utils.db_connection import DbConnection


class FavoriteStationDAO:
    """Gère l'accès aux données des stations favorites en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def add_favorite(self, user_id: int, station_id: str) -> bool:
        """
        Ajoute une station aux favoris d'un utilisateur.

        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur.
        station_id : str
            Identifiant de la station à ajouter aux favoris.

        Returns
        -------
        bool
            True si l'ajout a réussi.
        """
        conn = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO user_favorite_station (user_id, station_id)
                        SELECT u.user_id, s.station_id
                        FROM "user" AS u
                        CROSS JOIN station_information AS s
                        WHERE u.user_id = %(user_id)s
                          AND s.station_id = %(station_id)s
                        ON CONFLICT (user_id, station_id) DO NOTHING
                        RETURNING station_id
                        """,
                        {"user_id": user_id, "station_id": station_id},
                    )
                    added = cursor.fetchone() is not None
                conn.commit()
                return added
        except Exception:
            if conn is not None:
                conn.rollback()
            raise

    def list_favorites(self, query_params: dict) -> list[StationInformation]:
        """
        Liste les stations favorites d'un utilisateur.

        Parameters
        ----------
        query_params: dict
            Identifiant de l'utilisateur.

        Returns
        -------
        list of StationInformation
            Liste des stations favorites de l'utilisateur.
            Ne renvoie rien si l'utilisateur n'est pas reconnu avec son identifiant.
        """
        user_id = query_params["user_id"]

        conn = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        'SELECT 1 FROM "user" WHERE user_id = %(user_id)s',
                        {"user_id": user_id},
                    )
                    if cursor.fetchone() is None:
                        conn.commit()
                        return None

                    cursor.execute(
                        """
                        SELECT
                            s.station_id,
                            s.name,
                            s.short_name,
                            s.lat,
                            s.lon,
                            s.adress AS address,
                            s.is_virtual_station,
                            s.station_area,
                            s.contact_phone,
                            s.capacity,
                            s.is_charging_station
                        FROM user_favorite_station AS f
                        JOIN station_information AS s
                          ON s.station_id = f.station_id
                        WHERE f.user_id = %(user_id)s
                        ORDER BY f.created_at DESC, s.station_id
                        """,
                        {"user_id": user_id},
                    )
                    rows = cursor.fetchall()
                    conn.commit()
                    return [StationInformation(**row) for row in rows]
        except Exception:
            if conn is not None:
                conn.rollback()
            raise

    def count_favorites(self, station_ids: list[str]) -> dict[str, int]:
        """
        Compte le nombre d'utilisateurs ayant mis chaque station en favori.

        Parameters
        ----------
        station_ids : list of str
            Identifiants des stations concernées.

        Returns
        -------
        dict
            Dictionnaire associant chaque identifiant de station à son
            nombre de favoris.
            Ne renvoie rien si un ou plusieurs identifiants de stations ne sont
            pas reconnus.
        """
        if not station_ids:
            return {}

        conn = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT s.station_id, COUNT(f.user_id) AS favorite_count
                        FROM station_information AS s
                        LEFT JOIN user_favorite_station AS f
                          ON f.station_id = s.station_id
                        WHERE s.station_id = ANY(%(station_ids)s)
                        GROUP BY s.station_id
                        """,
                        {"station_ids": station_ids},
                    )
                    rows = cursor.fetchall()
                    counts = {
                        row["station_id"]: row["favorite_count"] for row in rows
                    }
                    if len(counts) != len(set(station_ids)):
                        conn.commit()
                        return None
                    conn.commit()
                    return counts
        except Exception:
            if conn is not None:
                conn.rollback()
            raise

    def remove_favorite(self, user_id: int, station_id: str) -> bool:
        """
        Retire une station des favoris d'un utilisateur.

        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur.
        station_id : str
            Identifiant de la station à retirer des favoris.

        Returns
        -------
        bool
            True si le retrait a réussi.
        """
        conn = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM user_favorite_station
                        WHERE user_id = %(user_id)s
                          AND station_id = %(station_id)s
                        RETURNING station_id
                        """,
                        {"user_id": user_id, "station_id": station_id},
                    )
                    removed = cursor.fetchone() is not None
                conn.commit()
                return removed
        except Exception:
            if conn is not None:
                conn.rollback()
            raise

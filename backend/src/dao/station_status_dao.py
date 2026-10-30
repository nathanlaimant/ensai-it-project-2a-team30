from collections import defaultdict
from datetime import datetime

from psycopg2.extras import Json, execute_values

from business_object.station_status import StationStatus
from utils.db_connection import DbConnection
from utils.log_utils import get_logger

logger = get_logger(__name__)


class StationStatusDAO:
    """Gère l'accès aux données de statut des stations en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def bulk_insert_status(self, records: list[StationStatus]) -> int:
        """
        Insère en masse une liste d'enregistrements de statut de stations.

        Parameters
        ----------
        records : list of StationStatus
            Enregistrements de statut à insérer.

        Returns
        -------
        int
            Nombre d'enregistrements effectivement insérés.
        """
        if not records:
            return 0

        logger.info(f"Bulk inserting {len(records)} station status records.")
        query = """
            INSERT INTO station_status (
                station_id,
                num_bikes_available,
                num_bikes_disabled,
                num_docks_available,
                num_docks_disabled,
                operational_capacity,
                last_reported,
                vehicle_types_available,
                vehicle_docks_available,
                station_state
            ) VALUES %s
            ON CONFLICT (station_id, last_reported) DO NOTHING
            RETURNING station_status_id;
        """

        data = [
            (
                r.station_id,
                r.num_bikes_available,
                r.num_bikes_disabled,
                r.num_docks_available,
                r.num_docks_disabled,
                r.operational_capacity,
                r.last_reported,
                Json(r.vehicle_types_available) if r.vehicle_types_available else None,
                Json(r.vehicle_docks_available) if r.vehicle_docks_available else None,
                r.station_state,
            )
            for r in records
        ]

        res = 0
        try:
            with self._db_connection.get_connection() as conn:
                with conn:
                    with conn.cursor() as cursor:
                        inserted_ids = execute_values(
                            cur=cursor,
                            sql=query,
                            argslist=data,
                            template=None,
                            page_size=1000,
                            fetch=True,
                        )
                        res = len(inserted_ids)
        except Exception as e:
            logger.error(e)

        logger.info(f"Successfully inserted {res} station status records.")
        return res

    def get_latest_status(self, station_id: str) -> StationStatus | None:
        """
        Récupère le dernier statut connu d'une station.

        Parameters
        ----------
        station_id : str
            Identifiant de la station concernée.

        Returns
        -------
        StationStatus | None
            Dernier statut connu de la station, ou None si introuvable.
        """
        row = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT *
                        FROM station_status
                        WHERE station_id = %s
                        ORDER BY last_reported DESC
                        LIMIT 1;
                    """
                    cursor.execute(query, (station_id,))
                    row = cursor.fetchone()
        except Exception as e:
            logger.error(e)

        if row:
            return StationStatus(
                station_status_id=row["station_status_id"],
                station_id=row["station_id"],
                num_bikes_available=row["num_bikes_available"],
                num_bikes_disabled=row["num_bikes_disabled"],
                num_docks_available=row["num_docks_available"],
                num_docks_disabled=row["num_docks_disabled"],
                operational_capacity=row["operational_capacity"],
                last_reported=row["last_reported"],
                vehicle_types_available=row["vehicle_types_available"],
                vehicle_docks_available=row["vehicle_docks_available"],
                station_state=row["station_state"],
            )
        return None

    def get_one_station_history(
        self, station_id: str, start_time: datetime, end_time: datetime
    ) -> list[StationStatus]:
        """
        Récupère l'historique des statuts d'une station sur une période donnée.

        Parameters
        ----------
        station_id : str
            Identifiant de la station concernée.
        start_time : datetime
            Date et heure de début de la période.
        end_time : datetime
            Date et heure de fin de la période (exclusif).

        Returns
        -------
        list of StationStatus
            Liste des statuts de la station sur la période demandée,
            triés par last_reported croissante.
            Renvoie une liste vide si la station est introuvable ou si les bornes chronologiques
            ne sont pas disponibles dans la base de données.
        """
        res = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT *
                        FROM station_status
                        WHERE station_id = %s
                        AND last_reported >= %s
                        AND last_reported < %s
                        ORDER BY last_reported ASC;
                    """
                    cursor.execute(query, (station_id, start_time, end_time))
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)

        station_statuses = []
        if res:
            for row in res:
                station_status = StationStatus(
                    station_status_id=row["station_status_id"],
                    station_id=row["station_id"],
                    num_bikes_available=row["num_bikes_available"],
                    num_bikes_disabled=row["num_bikes_disabled"],
                    num_docks_available=row["num_docks_available"],
                    num_docks_disabled=row["num_docks_disabled"],
                    operational_capacity=row["operational_capacity"],
                    last_reported=row["last_reported"],
                    vehicle_types_available=row["vehicle_types_available"],
                    vehicle_docks_available=row["vehicle_docks_available"],
                    station_state=row["station_state"],
                )
                station_statuses.append(station_status)
        return station_statuses

    def get_all_station_history(
        self, start_time: datetime, end_time: datetime
    ) -> dict[str, list[StationStatus]]:
        """
        Récupère l'historique des statuts des stations sur une période donnée.

        Parameters
        ----------
        start_time : datetime
            Date et heure de début de la période.
        end_time : datetime
            Date et heure de fin de la période (exclusif).

        Returns
        -------
        dict[str, list[StationStatus]]
            Dictionnaire avec clé=(ID de la station) et valeur=(la liste des statuts)
            de cette station sur la période demandée, triés par last_reported croissante.
            Renvoie un dictionnaire vide si aucune station n'est trouvée ou si les bornes
            chronologiques ne sont pas disponibles dans la base de données.
        """
        res = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                            SELECT *
                            FROM station_status
                            WHERE last_reported >= %s
                            AND last_reported < %s
                            ORDER BY last_reported ASC;
                        """
                    cursor.execute(query, (start_time, end_time))
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)

        history: defaultdict[str, list[StationStatus]] = defaultdict(list)
        if res:
            for row in res:
                station_status = StationStatus(
                    station_status_id=row["station_status_id"],
                    station_id=row["station_id"],
                    num_bikes_available=row["num_bikes_available"],
                    num_bikes_disabled=row["num_bikes_disabled"],
                    num_docks_available=row["num_docks_available"],
                    num_docks_disabled=row["num_docks_disabled"],
                    operational_capacity=row["operational_capacity"],
                    last_reported=row["last_reported"],
                    vehicle_types_available=row["vehicle_types_available"],
                    vehicle_docks_available=row["vehicle_docks_available"],
                    station_state=row["station_state"],
                )
                history[station_status.station_id].append(station_status)
        return history

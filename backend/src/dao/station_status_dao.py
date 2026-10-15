from datetime import datetime

from psycopg2.extras import Json, execute_values

from business_object.station_status import StationStatus
from utils.db_connection import DbConnection
from utils.log_utils import get_logger, log

logger = get_logger(__name__)


class StationStatusDAO:
    """Gère l'accès aux données de statut des stations en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    @log
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

        query = """
            INSERT INTO station_status (
                station_id,
                num_bikes_available,
                num_bikes_disabled,
                num_docks_available,
                num_docks_disabled,
                operational_capacity,
                is_installed,
                is_renting,
                is_returning,
                last_reported,
                vehicle_types_available,
                vehicle_docks_available,
                station_state
            ) VALUES %
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
                r.is_installed,
                r.is_renting,
                r.is_returning,
                r.last_reported,
                Json(r.vehicle_types_available) if r.vehicle_types_available else None,
                Json(r.vehicle_docks_available) if r.vehicle_docks_available else None,
                r.station_state,
            )
            for r in records
        ]

        try:
            with self._db_connection.get_connection() as conn:
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
                station_status_id=row[0],
                station_id=row[1],
                num_bikes_available=row[2],
                num_bikes_disabled=row[3],
                num_docks_available=row[4],
                num_docks_disabled=row[5],
                operational_capacity=row[6],
                is_installed=row[7],
                is_renting=row[8],
                is_returning=row[9],
                last_reported=row[10],
                vehicle_types_available=row[11],
                vehicle_docks_available=row[12],
                station_state=row[13],
            )
        return None

    def get_status_history(
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
            Date et heure de fin de la période.

        Returns
        -------
        list of StationStatus
            Liste des statuts de la station sur la période demandée.
            Renvoie une liste vide si la station est introuvable ou si les bornes chronologiques
            ne sont pas disponibles dans la base de données.
        """
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT *
                        FROM station_status
                        WHERE station_id = %s
                        AND last_reported BETWEEN %s AND %s
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
                    station_status_id=row[0],
                    station_id=row[1],
                    num_bikes_available=row[2],
                    num_bikes_disabled=row[3],
                    num_docks_available=row[4],
                    num_docks_disabled=row[5],
                    operational_capacity=row[6],
                    is_installed=row[7],
                    is_renting=row[8],
                    is_returning=row[9],
                    last_reported=row[10],
                    vehicle_types_available=row[11],
                    vehicle_docks_available=row[12],
                    station_state=row[13],
                )
                station_statuses.append(station_status)
        return station_statuses

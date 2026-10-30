from datetime import date, datetime, time

from psycopg2.extras import execute_values

from business_object.station_status_hourly import StationStatusHourly
from utils.db_connection import DbConnection
from utils.log_utils import get_logger

logger = get_logger(__name__)


class StationStatusHourlyDAO:
    """Gère l'accès aux données de statut des stations agrégées à l'heure en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def bulk_upsert_hourly_stats(self, records: list[StationStatusHourly]) -> int:
        """
        Insert en masse les données d'une station sur une heure.

        Parameters
        ----------
        records : list of StationStatusHourly
            Enregistrements d'agrégation horaire à insérer.

        Returns
        -------
        int
            Nombre d'enregistrements effectivement insérés.
        """
        if not records:
            return 0

        logger.info(f"Bulk upserting {len(records)} station hourly status records.")
        query = """
            INSERT INTO station_status_hourly (
                station_id,
                bucket_hour,
                sample_count,
                avg_operational_capacity,
                avg_num_bikes_available,
                avg_num_docks_available,
                empty_duration_sec,
                full_duration_sec,
                empty_events_cnt,
                full_events_cnt,
                reliability_score
            ) VALUES %s
            ON CONFLICT (station_id, bucket_hour)
            DO UPDATE SET
                sample_count = EXCLUDED.sample_count,
                avg_operational_capacity = EXCLUDED.avg_operational_capacity,
                avg_num_bikes_available = EXCLUDED.avg_num_bikes_available,
                avg_num_docks_available = EXCLUDED.avg_num_docks_available,
                empty_duration_sec = EXCLUDED.empty_duration_sec,
                full_duration_sec = EXCLUDED.full_duration_sec,
                empty_events_cnt = EXCLUDED.empty_events_cnt,
                full_events_cnt = EXCLUDED.full_events_cnt,
                reliability_score = EXCLUDED.reliability_score
            RETURNING station_id, bucket_hour;
        """

        data = [
            (
                r.station_id,
                r.bucket_hour,
                r.sample_count,
                r.avg_operational_capacity,
                r.avg_num_bikes_available,
                r.avg_num_docks_available,
                r.empty_duration_sec,
                r.full_duration_sec,
                r.empty_events_cnt,
                r.full_events_cnt,
                r.reliability_score,
            )
            for r in records
        ]

        res = 0
        try:
            with self._db_connection.get_connection() as conn:
                with conn:
                    with conn.cursor() as cursor:
                        upserted = execute_values(
                            cur=cursor,
                            sql=query,
                            argslist=data,
                            template=None,
                            page_size=1000,
                            fetch=True,
                        )
                        res = len(upserted)
        except Exception as e:
            logger.error(e)

        logger.info(f"Successfully upserted {res} station hourly status records.")
        return res

    def get_latest_hourly_status(self, station_id: str) -> StationStatusHourly | None:
        """
        Récupère le dernier enregistrement d'agrégation horaire d'une station.

        Parameters
        ----------
        station_id : str
            Identifiant de la station concernée.

        Returns
        -------
        StationStatusHourly | None
            Dernier enregistrement d'agrégation horaire de la station.
            Renvoie None si la station n'est pas identifiable.
        """
        row = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT *
                        FROM station_status_hourly
                        WHERE station_id = %s
                        ORDER BY bucket_hour DESC
                        LIMIT 1;
                    """
                    cursor.execute(query, (station_id,))
                    row = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            return None

        if row:
            return StationStatusHourly(
                station_id=row["station_id"],
                bucket_hour=row["bucket_hour"],
                sample_count=row["sample_count"],
                avg_operational_capacity=row["avg_operational_capacity"],
                avg_num_bikes_available=row["avg_num_bikes_available"],
                avg_num_docks_available=row["avg_num_docks_available"],
                empty_duration_sec=row["empty_duration_sec"],
                full_duration_sec=row["full_duration_sec"],
                empty_events_cnt=row["empty_events_cnt"],
                full_events_cnt=row["full_events_cnt"],
                reliability_score=row["reliability_score"],
            )
        return None

    def get_hourly_stats(
        self, station_id: str, start_time: datetime, end_time: datetime
    ) -> list[StationStatusHourly]:
        """Récupère les agrégations horaires d'une station sur une période donnée.

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
        list of StationStatusHourly
            Liste des agrégations horaires de la station sur la période demandée.
            Renvoie une liste vide si la station n'est pas identifiable ou si les bornes chronologiques
            ne sont pas présentes dans la base de données.
        """
        res = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT *
                        FROM station_status_hourly
                        WHERE station_id = %s
                        AND bucket_hour BETWEEN %s AND %s
                        ORDER BY bucket_hour ASC;
                    """
                    cursor.execute(query, (station_id, start_time, end_time))
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)

        station_statuses = []
        if res:
            for row in res:
                station_status = StationStatusHourly(
                    station_id=row["station_id"],
                    bucket_hour=row["bucket_hour"],
                    sample_count=row["sample_count"],
                    avg_operational_capacity=row["avg_operational_capacity"],
                    avg_num_bikes_available=row["avg_num_bikes_available"],
                    avg_num_docks_available=row["avg_num_docks_available"],
                    empty_duration_sec=row["empty_duration_sec"],
                    full_duration_sec=row["full_duration_sec"],
                    empty_events_cnt=row["empty_events_cnt"],
                    full_events_cnt=row["full_events_cnt"],
                    reliability_score=row["reliability_score"],
                )
                station_statuses.append(station_status)
        return station_statuses

    def aggregate_daily_stats(
        self, station_id: str, start_date: date, end_date: date
    ) -> list[dict]:
        """
        Agrège les statistiques horaires d'une station à l'échelle journalière.

        Parameters
        ----------
        station_id : str
            Identifiant de la station concernée.
        start_date : date
            Date de début de la période.
        end_date : date
            Date de fin de la période.

        Returns
        -------
        list of dict
            Liste des statistiques journalières agrégées de la station.
            Renvoie une liste vide si la station n'est pas identifiable ou que les bornes chronologiques
            ne sont pas présentes dans la base de données.
            Les cles : stat_date, station_id, sample_count, avg_operational_capacity,
            avg_num_bikes_available, avg_num_docks_available, empty_duration_sec, full_duration,
            empty_events_cnt, full_events_cnt, avg_reliability_score
        """
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        res = None
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT
                            date_trunc('day', bucket_hour)::date AS stat_date,
                            station_id,
                            SUM(sample_count) AS sample_count,
                            ROUND(AVG(avg_operational_capacity)::real)::int AS avg_operational_capacity,
                            ROUND(AVG(avg_num_bikes_available)::real)::int AS avg_num_bikes_available,
                            ROUND(AVG(avg_num_docks_available)::real)::int AS avg_num_docks_available,
                            SUM(empty_duration_sec) AS empty_duration_sec,
                            SUM(full_duration_sec) AS full_duration_sec,
                            SUM(empty_events_cnt) AS empty_events_cnt,
                            SUM(full_events_cnt) AS full_events_cnt,
                            ROUND(AVG(reliability_score)::real)::int AS avg_reliability_score
                        FROM station_status_hourly
                        WHERE station_id = %s
                        AND bucket_hour BETWEEN %s AND %s
                        GROUP BY date_trunc('day', bucket_hour)::date, station_id
                        ORDER BY stat_date ASC;
                    """
                    cursor.execute(query, (station_id, start_datetime, end_datetime))
                    res = cursor.fetchall()
            if res:
                return [dict(row) for row in res]
        except Exception as e:
            logger.error(e)
        return []

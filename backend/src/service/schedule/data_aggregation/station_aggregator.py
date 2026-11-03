import time
from datetime import UTC, datetime, timedelta

from business_object.station_state import StationState
from business_object.station_status import StationStatus
from business_object.station_status_hourly import StationStatusHourly
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO
from utils.log_utils import get_logger

logger = get_logger(__name__)

# Poids utilisés pour le calcul du score de fiabilité.
EMPTY_PENALTY_WEIGHT = 0.55  # w_1 : poids de pénalité pour l'état "vide"
FULL_PENALTY_WEIGHT = 0.35  # w_2 : poids de pénalité pour l'état "plein"
PERSISTENCE_PENALTY_WEIGHT = 0.1  # w_3 : poids de pénalité pour les épisodes persistants


class StationAggregator:
    """
    Agrège les statuts en temps réel des stations en statistiques horaires.

    Parameters
    ----------
    station_status_dao : StationStatusDAO
        DAO permettant l'accès aux statuts en temps réel des stations.
    station_hourly_dao : StationStatusHourlyDAO
        DAO permettant l'accès aux agrégations horaires des stations.
    """

    def __init__(
        self,
        station_status_dao: StationStatusDAO,
        station_hourly_dao: StationStatusHourlyDAO,
    ):
        self.station_status_dao = station_status_dao
        self.station_hourly_dao = station_hourly_dao

    async def aggregate_hourly_stats(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> int:
        """
        Agrège les statuts en temps réel des stations sur l'heure écoulée
        et persiste le résultat sous forme d'agrégations horaires.

        Parameters
        ----------
        start_time : datetime | None, optional
            Heure de début du créneau horaire à agréger. Par défaut :
            end_time - timedelta(hours=1).
        end_time : datetime | None, optional
            Heure de fin du créneau horaire à agréger. Par défaut :
            datetime.now(UTC).replace(minute=0, second=0, microsecond=0).

        Returns
        -------
        int
            Nombre d'agrégations horaires persistées (insérées ou mises
            à jour) en base de données.
        """
        agg_start_perf = time.perf_counter()

        start_time, end_time = self._resolve_time_bucket(start_time, end_time)

        logger.info(
            "Aggregating hourly stats for bucket [%s, %s)",
            start_time.isoformat(),
            end_time.isoformat(),
        )

        raw_statuses = self.station_status_dao.get_all_station_history(
            start_time=start_time,
            end_time=end_time,
        )
        if not raw_statuses:
            logger.warning(
                "No station status records found for bucket [%s, %s)",
                start_time.isoformat(),
                end_time.isoformat(),
            )
            return 0

        hourly_records: list[StationStatusHourly] = []
        for station_id, statuses in raw_statuses.items():
            if not statuses:
                continue
            hourly_records.append(
                self._aggregate_station_stats(
                    station_id=station_id,
                    statuses=statuses,
                    start_time=start_time,
                    end_time=end_time,
                )
            )

        inserted_records = self.station_hourly_dao.bulk_upsert_hourly_stats(
            hourly_records
        )

        elapsed_sec = time.perf_counter() - agg_start_perf
        logger.info(
            "Aggregated %d stations into %d hourly stats in %.2f seconds",
            len(raw_statuses),
            inserted_records,
            elapsed_sec,
        )
        return inserted_records

    @staticmethod
    def _resolve_time_bucket(
        start_time: datetime | None,
        end_time: datetime | None,
    ) -> tuple[datetime, datetime]:
        """Calcule les bornes du créneau horaire à agréger.

        Si `end_time` n'est pas fourni, il correspond à l'heure courante
        (UTC) tronquée à l'heure pile. Si `start_time` n'est pas fourni,
        il correspond à `end_time - 1 heure`.

        Parameters
        ----------
        start_time : datetime | None
            Heure de début du créneau, ou None pour utiliser la valeur
            par défaut.
        end_time : datetime | None
            Heure de fin du créneau, ou None pour utiliser la valeur
            par défaut.

        Returns
        -------
        tuple of (datetime, datetime)
            Couple `(start_time, end_time)` résolu.
        """
        if end_time is None:
            now = datetime.now(UTC)
            end_time = now.replace(minute=0, second=0, microsecond=0)
        if start_time is None:
            start_time = end_time - timedelta(hours=1)
        return start_time, end_time

    def _aggregate_station_stats(
        self,
        station_id: str,
        statuses: list[StationStatus],
        start_time: datetime,
        end_time: datetime,
    ) -> StationStatusHourly:
        """Agrège les statuts d'une station sur un créneau horaire donné.

        Parameters
        ----------
        station_id : str
            Identifiant de la station concernée.
        statuses : list of StationStatus
            Statuts de la station sur le créneau, triés chronologiquement.
        start_time : datetime
            Heure de début du créneau horaire agrégé.
        end_time : datetime
            Heure de fin du créneau horaire agrégé.

        Returns
        -------
        StationStatusHourly
            Agrégation horaire calculée pour cette station.
        """
        sample_count = len(statuses)

        avg_operational_capacity, avg_num_bikes_available, avg_num_docks_available = (
            self._compute_basic_averages(statuses)
        )

        empty_duration_sec, full_duration_sec, empty_events_cnt, full_events_cnt = (
            self._compute_durations_and_events(statuses, start_time, end_time)
        )

        total_duration_sec = (end_time - start_time).total_seconds()
        reliability_score = self._compute_reliability_score(
            empty_duration_sec=empty_duration_sec,
            full_duration_sec=full_duration_sec,
            empty_events_cnt=empty_events_cnt,
            full_events_cnt=full_events_cnt,
            total_duration_sec=total_duration_sec,
        )

        return StationStatusHourly(
            station_id=station_id,
            bucket_hour=start_time,
            sample_count=sample_count,
            avg_operational_capacity=avg_operational_capacity,
            avg_num_bikes_available=avg_num_bikes_available,
            avg_num_docks_available=avg_num_docks_available,
            empty_duration_sec=empty_duration_sec,
            full_duration_sec=full_duration_sec,
            empty_events_cnt=empty_events_cnt,
            full_events_cnt=full_events_cnt,
            reliability_score=reliability_score,
        )

    @staticmethod
    def _compute_basic_averages(
        statuses: list[StationStatus],
    ) -> tuple[float, float, float]:
        """Calcule les moyennes de capacité, de vélos et de docks disponibles.

        Les valeurs `None` sont ignorées du calcul de moyenne (elles ne
        comptent ni dans la somme, ni dans le dénominateur).

        Parameters
        ----------
        statuses : list of StationStatus
            Statuts de la station sur le créneau à agréger.

        Returns
        -------
        tuple of (float, float, float)
            Moyennes `(avg_operational_capacity, avg_num_bikes_available,
            avg_num_docks_available)`, arrondies à 2 décimales. Vaut 0.0
            si aucune valeur n'était disponible.
        """
        sum_op_cap, count_op_cap = 0, 0
        sum_bikes, count_bikes = 0, 0
        sum_docks, count_docks = 0, 0

        for s in statuses:
            if s.operational_capacity is not None:
                sum_op_cap += s.operational_capacity
                count_op_cap += 1
            if s.num_bikes_available is not None:
                sum_bikes += s.num_bikes_available
                count_bikes += 1
            if s.num_docks_available is not None:
                sum_docks += s.num_docks_available
                count_docks += 1

        avg_operational_capacity = (
            round(sum_op_cap / count_op_cap, 2) if count_op_cap else 0.0
        )
        avg_num_bikes_available = (
            round(sum_bikes / count_bikes, 2) if count_bikes else 0.0
        )
        avg_num_docks_available = (
            round(sum_docks / count_docks, 2) if count_docks else 0.0
        )
        return avg_operational_capacity, avg_num_bikes_available, avg_num_docks_available

    @staticmethod
    def _compute_durations_and_events(
        statuses: list[StationStatus],
        start_time: datetime,
        end_time: datetime,
    ) -> tuple[int, int, int, int]:
        """Calcule les durées passées vide/pleine et le nombre d'épisodes associés.

        Chaque relevé de statut est supposé rester valide jusqu'au relevé
        suivant (ou jusqu'à `end_time` pour le dernier). Un "événement"
        est compté à chaque transition vers l'état vide ou plein.

        Parameters
        ----------
        statuses : list of StationStatus
            Statuts de la station sur le créneau, triés chronologiquement.
        start_time : datetime
            Heure de début du créneau horaire agrégé.
        end_time : datetime
            Heure de fin du créneau horaire agrégé.

        Returns
        -------
        tuple of (int, int, int, int)
            `(empty_duration_sec, full_duration_sec, empty_events_cnt,
            full_events_cnt)`, les incohérences entre durée nulle et
            nombre d'événements étant corrigées (une durée positive
            implique au moins un événement, et inversement).
        """
        sample_count = len(statuses)
        st, et = start_time, end_time

        empty_duration_sec_float = 0.0
        full_duration_sec_float = 0.0
        empty_events_cnt = 0
        full_events_cnt = 0
        prev_state = None

        for i, s in enumerate(statuses):
            curr_state = (s.station_state or "").upper()

            # Comptage des événements (transitions d'état)
            if curr_state == StationState.EMPTY and prev_state != StationState.EMPTY:
                empty_events_cnt += 1
            elif curr_state == StationState.FULL and prev_state != StationState.FULL:
                full_events_cnt += 1
            prev_state = curr_state

            # Durée couverte par ce relevé
            if sample_count == 1:
                dt = (et - st).total_seconds()
            else:
                t_start_i = st if i == 0 else s.last_reported
                t_end_i = statuses[i + 1].last_reported if i < sample_count - 1 else et
                dt = max(0.0, (t_end_i - t_start_i).total_seconds())

            if curr_state == StationState.EMPTY:
                empty_duration_sec_float += dt
            elif curr_state == StationState.FULL:
                full_duration_sec_float += dt

        empty_duration_sec = int(round(empty_duration_sec_float))
        full_duration_sec = int(round(full_duration_sec_float))

        # Correction des incohérences entre durée et nombre d'événements
        if empty_duration_sec > 0 and empty_events_cnt == 0:
            empty_events_cnt = 1
        if full_duration_sec > 0 and full_events_cnt == 0:
            full_events_cnt = 1
        if empty_duration_sec == 0:
            empty_events_cnt = 0
        if full_duration_sec == 0:
            full_events_cnt = 0

        return empty_duration_sec, full_duration_sec, empty_events_cnt, full_events_cnt

    @staticmethod
    def _compute_reliability_score(
        empty_duration_sec: int,
        full_duration_sec: int,
        empty_events_cnt: int,
        full_events_cnt: int,
        total_duration_sec: float,
    ) -> float:
        """Calcule le score de fiabilité d'une station sur un créneau horaire.

        Le score pénalise le temps passé vide (`P_empty`) et plein
        (`P_full`), ainsi que la durée moyenne des épisodes persistants
        (`D_penalty`), selon la formule :
        `score = max(0, 100 - (w_1 * P_empty + w_2 * P_full
        + w_3 * min(100, D_penalty)))`.

        Parameters
        ----------
        empty_duration_sec : int
            Durée totale (en secondes) passée dans l'état "vide".
        full_duration_sec : int
            Durée totale (en secondes) passée dans l'état "plein".
        empty_events_cnt : int
            Nombre d'épisodes où la station est devenue vide.
        full_events_cnt : int
            Nombre d'épisodes où la station est devenue pleine.
        total_duration_sec : float
            Durée totale (en secondes) du créneau horaire agrégé.

        Returns
        -------
        float
            Score de fiabilité, borné entre 0.0 et 100.0, arrondi à
            2 décimales.
        """
        if total_duration_sec <= 0:
            return 0.0

        p_empty = (empty_duration_sec / total_duration_sec) * 100.0
        p_full = (full_duration_sec / total_duration_sec) * 100.0

        # Durée moyenne (en minutes) des épisodes vide/plein
        d_empty = (
            (empty_duration_sec / 60.0) / empty_events_cnt
            if empty_events_cnt > 0
            else 0.0
        )
        d_full = (
            (full_duration_sec / 60.0) / full_events_cnt
            if full_events_cnt > 0
            else 0.0
        )
        d_penalty = d_empty + d_full

        score = max(
            0.0,
            100.0
            - (
                EMPTY_PENALTY_WEIGHT * p_empty
                + FULL_PENALTY_WEIGHT * p_full
                + PERSISTENCE_PENALTY_WEIGHT * min(100.0, d_penalty)
            ),
        )
        return round(score, 2)

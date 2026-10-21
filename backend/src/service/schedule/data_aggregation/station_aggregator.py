import time
from datetime import UTC, datetime, timedelta

from business_object.station_state import StationState
from business_object.station_status_hourly import StationStatusHourly
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO
from utils.log_utils import get_logger

logger = get_logger(__name__)


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
            Nombre d'agrégations horaires insérées en base de données.
        """
        agg_start_perf = time.perf_counter()

        # 1. Calculate bucket hour:
        # start_time = current_hour - 1 hour
        # end_time = current_hour
        if end_time is None:
            now = datetime.now(UTC)
            end_time = now.replace(minute=0, second=0, microsecond=0)
        if start_time is None:
            start_time = end_time - timedelta(hours=1)

        logger.info(
            "Aggregating hourly stats for bucket [%s, %s)",
            start_time.isoformat(),
            end_time.isoformat(),
        )

        # 2. Read raw statuses sorted and grouped by station_id from DB:
        # Call station_status_dao.get_all_station_history
        # If there is no record, log warn and return 0.
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

        # 3. Aggregate stats for each station
        hourly_records: list[StationStatusHourly] = []

        for station_id, statuses in raw_statuses.items():
            sample_count = len(statuses)
            if sample_count == 0:
                continue

            st = start_time
            et = end_time

            # Accumulators for averages
            sum_op_cap, count_op_cap = 0, 0
            sum_bikes, count_bikes = 0, 0
            sum_docks, count_docks = 0, 0

            # Accumulators for durations and events
            empty_duration_sec_float = 0.0
            full_duration_sec_float = 0.0
            empty_events_cnt = 0
            full_events_cnt = 0
            prev_state = None

            # Loop over statuses: basic stats, events, and durations
            for i, s in enumerate(statuses):
                # a. Basic stats accumulation
                if s.operational_capacity is not None:
                    sum_op_cap += s.operational_capacity
                    count_op_cap += 1
                if s.num_bikes_available is not None:
                    sum_bikes += s.num_bikes_available
                    count_bikes += 1
                if s.num_docks_available is not None:
                    sum_docks += s.num_docks_available
                    count_docks += 1

                # b. Events counting (transitions of state)
                curr_state = (s.station_state or "").upper()
                if (
                    curr_state == StationState.EMPTY
                    and prev_state != StationState.EMPTY
                ):
                    empty_events_cnt += 1
                elif (
                    curr_state == StationState.FULL and prev_state != StationState.FULL
                ):
                    full_events_cnt += 1
                prev_state = curr_state

                # c. Durations
                if sample_count == 1:
                    dt = (et - st).total_seconds()
                else:
                    t_start_i = st if i == 0 else s.last_reported
                    t_end_i = (
                        statuses[i + 1].last_reported if i < sample_count - 1 else et
                    )
                    dt = max(0.0, (t_end_i - t_start_i).total_seconds())

                if curr_state == StationState.EMPTY:
                    empty_duration_sec_float += dt
                elif curr_state == StationState.FULL:
                    full_duration_sec_float += dt

            # Finalize averages
            avg_operational_capacity = (
                round(sum_op_cap / count_op_cap, 2) if count_op_cap else 0.0
            )
            avg_num_bikes_available = (
                round(sum_bikes / count_bikes, 2) if count_bikes else 0.0
            )
            avg_num_docks_available = (
                round(sum_docks / count_docks, 2) if count_docks else 0.0
            )

            # Finalize durations
            empty_duration_sec = int(round(empty_duration_sec_float))
            full_duration_sec = int(round(full_duration_sec_float))

            # Fix inconsistencies
            if empty_duration_sec > 0 and empty_events_cnt == 0:
                empty_events_cnt = 1
            if full_duration_sec > 0 and full_events_cnt == 0:
                full_events_cnt = 1
            if empty_duration_sec == 0:
                empty_events_cnt = 0
            if full_duration_sec == 0:
                full_events_cnt = 0

            # d. Calculate reliability_score:
            # P_empty = (empty_duration_sec / 3600.0) * 100
            # P_full  = (full_duration_sec / 3600.0) * 100
            total_duration_sec = (et - st).total_seconds()
            p_empty = (empty_duration_sec / total_duration_sec) * 100.0
            p_full = (full_duration_sec / total_duration_sec) * 100.0

            # Weights
            a = 1.0
            b = 1.0
            w_1 = 0.55  # w_1 = 0.55 (penalty weight of empty)
            w_2 = 0.35  # w_2 = 0.35 (penalty weight of full)
            w_3 = 0.1  # w_3 = 0.1 (penalty weight for persistent episodes)

            # D_penalty (in minutes) = (a * empty_duration_sec / empty_events_cnt) + (b * full_duration_sec / full_events_cnt)
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
            d_penalty = a * d_empty + b * d_full

            # Score = max(0.0, 100.0 - (w_1 * P_empty + w_2 * P_full + w_3 * min(100, D_penalty)))
            score = max(
                0.0,
                100.0 - (w_1 * p_empty + w_2 * p_full + w_3 * min(100.0, d_penalty)),
            )
            reliability_score = round(score, 2)

            # e. Init StationStatusHourly:
            hourly_obj = StationStatusHourly(
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
            hourly_records.append(hourly_obj)

        # 4. Bulk Insert
        inserted_records = self.station_hourly_dao.bulk_insert_hourly_stats(
            hourly_records
        )

        # 5. Ending
        # Log (no of stations aggregated, agg time,...)
        # Return no of records.
        elapsed_sec = time.perf_counter() - agg_start_perf
        logger.info(
            "Aggregated %d stations into %d hourly stats in %.2f seconds",
            len(raw_statuses),
            inserted_records,
            elapsed_sec,
        )
        return inserted_records

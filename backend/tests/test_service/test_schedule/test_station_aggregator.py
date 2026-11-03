"""
Tests unitaires pour StationAggregator et ses méthodes internes
(_resolve_time_bucket, _compute_basic_averages, _compute_durations_and_events,
_compute_reliability_score, _aggregate_station_stats, aggregate_hourly_stats).
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from business_object.station_state import StationState
from business_object.station_status import StationStatus
from business_object.station_status_hourly import StationStatusHourly
from service.schedule.data_aggregation.station_aggregator import StationAggregator

START = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)
END = START + timedelta(hours=1)


def make_status(
    station_state: str,
    last_reported: datetime,
    operational_capacity: int | None = 20,
    num_bikes_available: int | None = 5,
    num_docks_available: int | None = 15,
) -> StationStatus:
    """Construit un StationStatus minimal pour les tests, en ne faisant
    varier que les champs pertinents pour l'agrégation.
    """
    return StationStatus(
        station_status_id=1,
        station_id="station_1",
        num_bikes_available=num_bikes_available,
        num_bikes_disabled=0,
        num_docks_available=num_docks_available,
        num_docks_disabled=0,
        operational_capacity=operational_capacity,
        is_installed=True,
        is_renting=True,
        is_returning=True,
        last_reported=last_reported,
        vehicle_types_available=[],
        vehicle_docks_available=[],
        station_state=station_state,
    )


@pytest.fixture
def aggregator() -> StationAggregator:
    """Fournit un StationAggregator avec des DAO mockés."""
    return StationAggregator(
        station_status_dao=MagicMock(),
        station_hourly_dao=MagicMock(),
    )


class TestResolveTimeBucket:
    def test_both_none_returns_last_full_hour(self):
        """Si aucune borne n'est fournie, le créneau doit être [h-1, h]
        avec h = heure courante tronquée à l'heure pile.
        """
        resolved_start, resolved_end = StationAggregator._resolve_time_bucket(
            None, None
        )

        assert resolved_end.minute == 0
        assert resolved_end.second == 0
        assert resolved_end.microsecond == 0
        assert resolved_start == resolved_end - timedelta(hours=1)

    def test_end_time_given_start_time_defaults_to_one_hour_before(self):
        """Si seul end_time est fourni, start_time doit être calculé
        comme end_time - 1 heure.
        """
        resolved_start, resolved_end = StationAggregator._resolve_time_bucket(
            None, END
        )

        assert resolved_end == END
        assert resolved_start == END - timedelta(hours=1)

    def test_both_provided_are_returned_unchanged(self):
        """Si les deux bornes sont fournies, elles doivent être retournées
        telles quelles, sans recalcul.
        """
        resolved_start, resolved_end = StationAggregator._resolve_time_bucket(
            START, END
        )

        assert resolved_start == START
        assert resolved_end == END

class TestComputeBasicAverages:
    def test_averages_with_all_values_present(self):
        statuses = [
            make_status(
                StationState.FUNCTIONAL,
                START,
                operational_capacity=20,
                num_bikes_available=4,
                num_docks_available=16,
            ),
            make_status(
                StationState.FUNCTIONAL,
                START + timedelta(minutes=10),
                operational_capacity=20,
                num_bikes_available=6,
                num_docks_available=14,
            ),
        ]

        avg_cap, avg_bikes, avg_docks = StationAggregator._compute_basic_averages(
            statuses
        )

        assert avg_cap == 20.0
        assert avg_bikes == 5.0
        assert avg_docks == 15.0

    def test_none_values_are_excluded_from_average(self):
        """Une valeur None ne doit compter ni dans la somme ni dans le
        dénominateur de la moyenne.
        """
        statuses = [
            make_status(
                StationState.FUNCTIONAL,
                START,
                operational_capacity=None,
                num_bikes_available=10,
                num_docks_available=None,
            ),
            make_status(
                StationState.FUNCTIONAL,
                START + timedelta(minutes=10),
                operational_capacity=20,
                num_bikes_available=None,
                num_docks_available=10,
            ),
        ]

        avg_cap, avg_bikes, avg_docks = StationAggregator._compute_basic_averages(
            statuses
        )

        assert avg_cap == 20.0  # une seule valeur non-None
        assert avg_bikes == 10.0  # une seule valeur non-None
        assert avg_docks == 10.0  # une seule valeur non-None

    def test_all_none_returns_zero(self):
        statuses = [
            make_status(
                StationState.FUNCTIONAL,
                START,
                operational_capacity=None,
                num_bikes_available=None,
                num_docks_available=None,
            ),
        ]

        avg_cap, avg_bikes, avg_docks = StationAggregator._compute_basic_averages(
            statuses
        )

        assert (avg_cap, avg_bikes, avg_docks) == (0.0, 0.0, 0.0)

class TestComputeDurationsAndEvents:
    def test_known_sequence_matches_expected_durations_and_events(self):
        """Scénario de référence : FUNCTIONAL (5 min) -> EMPTY (20 min,
        2 relevés) -> FULL (20 min), sur un créneau d'1 heure.

        Attendu :
        - empty_duration_sec = 1800 (30 min : de 10h05 à 10h35,
          couvrant les deux relevés EMPTY consécutifs)
        - full_duration_sec = 600 (10 min : de 10h50 à 11h00)
        - empty_events_cnt = 1 (une seule transition vers EMPTY)
        - full_events_cnt = 1 (une seule transition vers FULL)
        """
        statuses = [
            make_status(StationState.FUNCTIONAL, START + timedelta(minutes=5)),
            make_status(StationState.EMPTY, START + timedelta(minutes=20)),
            make_status(StationState.EMPTY, START + timedelta(minutes=30)),
            make_status(StationState.FULL, START + timedelta(minutes=50)),
        ]

        empty_dur, full_dur, empty_cnt, full_cnt = (
            StationAggregator._compute_durations_and_events(statuses, START, END)
        )

        assert empty_dur == 1800
        assert full_dur == 600
        assert empty_cnt == 1
        assert full_cnt == 1

    def test_single_sample_covers_entire_bucket(self):
        """Avec un seul relevé, sa durée doit couvrir tout le créneau."""
        statuses = [make_status(StationState.EMPTY, START + timedelta(minutes=30))]

        empty_dur, full_dur, empty_cnt, full_cnt = (
            StationAggregator._compute_durations_and_events(statuses, START, END)
        )

        assert empty_dur == 3600  # toute l'heure
        assert full_dur == 0
        assert empty_cnt == 1
        assert full_cnt == 0

    def test_always_functional_gives_zero_durations_and_events(self):
        statuses = [
            make_status(StationState.FUNCTIONAL, START + timedelta(minutes=10)),
            make_status(StationState.FUNCTIONAL, START + timedelta(minutes=40)),
        ]

        empty_dur, full_dur, empty_cnt, full_cnt = (
            StationAggregator._compute_durations_and_events(statuses, START, END)
        )

        assert (empty_dur, full_dur, empty_cnt, full_cnt) == (0, 0, 0, 0)

    def test_repeated_same_state_counts_as_a_single_event(self):
        """Plusieurs relevés consécutifs dans le même état ne doivent
        compter que comme un seul événement (pas de nouvelle transition).
        """
        statuses = [
            make_status(StationState.EMPTY, START + timedelta(minutes=10)),
            make_status(StationState.EMPTY, START + timedelta(minutes=20)),
            make_status(StationState.EMPTY, START + timedelta(minutes=30)),
        ]

        _, _, empty_cnt, _ = StationAggregator._compute_durations_and_events(
            statuses, START, END
        )

        assert empty_cnt == 1

class TestComputeReliabilityScore:
    def test_score_matches_manual_calculation(self):
        """Vérifie le score sur le scénario de référence
        (empty=1800s, full=600s, 1 événement chacun, créneau de 3600s) :

        P_empty = 1800/3600*100 = 50.0
        P_full  = 600/3600*100  = 16.666...
        d_empty = (1800/60)/1 = 30.0 min
        d_full  = (600/60)/1  = 10.0 min
        d_penalty = 40.0 (non plafonné, < 100)
        score = 100 - (0.55*50 + 0.35*16.666... + 0.1*40)
              = 100 - (27.5 + 5.8333... + 4.0)
              = 100 - 37.3333...
              = 62.6666... -> arrondi à 62.67
        """
        score = StationAggregator._compute_reliability_score(
            empty_duration_sec=1800,
            full_duration_sec=600,
            empty_events_cnt=1,
            full_events_cnt=1,
            total_duration_sec=3600.0,
        )

        assert score == 62.67

    def test_perfect_station_scores_100(self):
        """Aucune durée vide ni pleine -> score maximal de 100."""
        score = StationAggregator._compute_reliability_score(
            empty_duration_sec=0,
            full_duration_sec=0,
            empty_events_cnt=0,
            full_events_cnt=0,
            total_duration_sec=3600.0,
        )

        assert score == 100.0

    def test_score_floors_at_zero_for_extreme_values(self):
        """Pour des valeurs extrêmes (station à la fois considérée vide et
        pleine sur tout le créneau, avec une pénalité de persistance
        plafonnée à 100), le score ne doit jamais descendre sous 0.0.
        """
        score = StationAggregator._compute_reliability_score(
            empty_duration_sec=3600,
            full_duration_sec=3600,
            empty_events_cnt=1,
            full_events_cnt=1,
            total_duration_sec=3600.0,
        )

        assert score == 0.0

    def test_zero_total_duration_returns_zero_without_error(self):
        """Un créneau de durée nulle ne doit pas lever de ZeroDivisionError
        et doit retourner un score de 0.0.
        """
        score = StationAggregator._compute_reliability_score(
            empty_duration_sec=0,
            full_duration_sec=0,
            empty_events_cnt=0,
            full_events_cnt=0,
            total_duration_sec=0.0,
        )

        assert score == 0.0

class TestAggregateStationStats:
    def test_combines_all_substeps_into_a_station_status_hourly(self, aggregator):
        statuses = [
            make_status(StationState.FUNCTIONAL, START + timedelta(minutes=5)),
            make_status(StationState.EMPTY, START + timedelta(minutes=20)),
            make_status(StationState.EMPTY, START + timedelta(minutes=30)),
            make_status(StationState.FULL, START + timedelta(minutes=50)),
        ]

        result = aggregator._aggregate_station_stats(
            station_id="station_1",
            statuses=statuses,
            start_time=START,
            end_time=END,
        )

        assert isinstance(result, StationStatusHourly)
        assert result.station_id == "station_1"
        assert result.bucket_hour == START
        assert result.sample_count == 4
        assert result.empty_duration_sec == 1800
        assert result.full_duration_sec == 600
        assert result.empty_events_cnt == 1
        assert result.full_events_cnt == 1
        assert result.reliability_score == 62.67

class TestAggregateHourlyStats:
    @pytest.mark.asyncio
    async def test_returns_zero_and_skips_upsert_when_no_data(self, aggregator):
        aggregator.station_status_dao.get_all_station_history.return_value = {}

        result = await aggregator.aggregate_hourly_stats(START, END)

        assert result == 0
        aggregator.station_hourly_dao.bulk_upsert_hourly_stats.assert_not_called()

    @pytest.mark.asyncio
    async def test_aggregates_each_station_and_persists_all_records(self, aggregator):
        statuses_station_1 = [
            make_status(StationState.FUNCTIONAL, START + timedelta(minutes=5)),
            make_status(StationState.EMPTY, START + timedelta(minutes=20)),
        ]
        statuses_station_2 = [
            make_status(StationState.FULL, START + timedelta(minutes=10)),
        ]
        aggregator.station_status_dao.get_all_station_history.return_value = {
            "station_1": statuses_station_1,
            "station_2": statuses_station_2,
        }
        aggregator.station_hourly_dao.bulk_upsert_hourly_stats.return_value = 2

        result = await aggregator.aggregate_hourly_stats(START, END)

        assert result == 2
        aggregator.station_status_dao.get_all_station_history.assert_called_once_with(
            start_time=START, end_time=END
        )

        persisted_records = (
            aggregator.station_hourly_dao.bulk_upsert_hourly_stats.call_args[0][0]
        )
        assert len(persisted_records) == 2
        persisted_station_ids = {record.station_id for record in persisted_records}
        assert persisted_station_ids == {"station_1", "station_2"}

    @pytest.mark.asyncio
    async def test_skips_stations_with_empty_status_list(self, aggregator):
        """Une station associée à une liste de statuts vide ne doit pas
        être incluse dans les enregistrements persistés.
        """
        aggregator.station_status_dao.get_all_station_history.return_value = {
            "station_1": [],
            "station_2": [make_status(StationState.FUNCTIONAL, START)],
        }
        aggregator.station_hourly_dao.bulk_upsert_hourly_stats.return_value = 1

        await aggregator.aggregate_hourly_stats(START, END)

        persisted_records = (
            aggregator.station_hourly_dao.bulk_upsert_hourly_stats.call_args[0][0]
        )
        assert len(persisted_records) == 1
        assert persisted_records[0].station_id == "station_2"

    @pytest.mark.asyncio
    async def test_uses_default_time_bucket_when_none_provided(self, aggregator):
        aggregator.station_status_dao.get_all_station_history.return_value = {}

        await aggregator.aggregate_hourly_stats()

        call_kwargs = aggregator.station_status_dao.get_all_station_history.call_args[
            1
        ]
        assert call_kwargs["end_time"] - call_kwargs["start_time"] == timedelta(
            hours=1
        )

from datetime import date, datetime
from pathlib import Path

import pytest

from business_object.station_information import StationInformation
from business_object.station_status_hourly import StationStatusHourly
from dao.station_dao import StationDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO
from utils.db_connection import DbConnection
from utils.settings import Settings

test_env_path = Path(__file__).resolve().parents[2] / ".test_env"


@pytest.fixture(scope="session")
def db_connection():
    """Fournit un pool de connexion à la base de données de test."""
    settings = Settings(
        _env_file=test_env_path if test_env_path.exists() else ".test_env"
    )
    return DbConnection(settings)


@pytest.fixture(scope="session")
def initiate_stations(db_connection):
    """Insère les stations pour toute la session de tests."""
    initial_stations = [
        StationInformation(
            station_id="245557155",
            name="Bischheim Gare",
            short_name="62000",
            lat=48.611639,
            lon=7.742056,
            address=None,
            is_virtual_station=False,
            station_area=None,
            contact_phone=None,
            capacity=5,
            is_charging_station=None,
        ),
        StationInformation(
            station_id="245557947",
            name="Bischheim Espace Européen",
            short_name="62001",
            lat=48.616361,
            lon=7.720056,
            address=None,
            is_virtual_station=False,
            station_area=None,
            contact_phone=None,
            capacity=10,
            is_charging_station=None,
        ),
    ]

    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM station_status_hourly;")
                cur.execute("DELETE FROM station_status;")
                cur.execute("DELETE FROM station_information;")

    station_dao = StationDAO(db_connection)
    for st in initial_stations:
        station_dao.upsert_station_info(st)

    yield initial_stations

    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM station_status_hourly;")
                cur.execute("DELETE FROM station_status;")
                cur.execute("DELETE FROM station_information;")


@pytest.fixture(autouse=True)
def setup_test_environment(db_connection, initiate_stations):
    """Nettoie la table station_status_hourly avant chaque test."""
    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM station_status_hourly;")


@pytest.fixture
def station_status_hourly_dao(db_connection):
    return StationStatusHourlyDAO(db_connection)


@pytest.fixture
def sample_hourly_stats():
    """Génère une liste isolée d'enregistrements horaires pour chaque test."""
    return [
        StationStatusHourly(
            station_id="245557155",
            bucket_hour=datetime.fromisoformat("2026-10-31 23:00:00+00:00"),
            sample_count=24,
            avg_operational_capacity=5.0,
            avg_num_bikes_available=4.5,
            avg_num_docks_available=0.5,
            empty_duration_sec=0,
            full_duration_sec=1200,
            empty_events_cnt=0,
            full_events_cnt=2,
            reliability_score=70.0,
        ),
        StationStatusHourly(
            station_id="245557155",
            bucket_hour=datetime.fromisoformat("2026-11-01 01:00:00+00:00"),
            sample_count=12,
            avg_operational_capacity=5.0,
            avg_num_bikes_available=2.5,
            avg_num_docks_available=2.5,
            empty_duration_sec=300,
            full_duration_sec=0,
            empty_events_cnt=1,
            full_events_cnt=0,
            reliability_score=85.0,
        ),
        StationStatusHourly(
            station_id="245557155",
            bucket_hour=datetime.fromisoformat("2026-11-01 02:00:00+00:00"),
            sample_count=12,
            avg_operational_capacity=5.0,
            avg_num_bikes_available=3.0,
            avg_num_docks_available=2.0,
            empty_duration_sec=0,
            full_duration_sec=600,
            empty_events_cnt=0,
            full_events_cnt=1,
            reliability_score=90.0,
        ),
        StationStatusHourly(
            station_id="245557947",
            bucket_hour=datetime.fromisoformat("2026-11-01 01:00:00+00:00"),
            sample_count=12,
            avg_operational_capacity=10.0,
            avg_num_bikes_available=6.0,
            avg_num_docks_available=4.0,
            empty_duration_sec=0,
            full_duration_sec=0,
            empty_events_cnt=0,
            full_events_cnt=0,
            reliability_score=100.0,
        ),
    ]


# Tests de bulk_upsert_hourly_stats()
def test_bulk_upsert_hourly_stats_ok(station_status_hourly_dao, sample_hourly_stats):
    """Insertions des statuts horaires des stations réussies"""
    # GIVEN
    number_records = len(sample_hourly_stats)
    # WHEN
    upserted_count = station_status_hourly_dao.bulk_upsert_hourly_stats(
        sample_hourly_stats
    )
    # THEN
    assert upserted_count == number_records


def test_bulk_upsert_hourly_stats_update_conflict(
    station_status_hourly_dao, sample_hourly_stats
):
    """Mise à jour réussie lors d'un conflit de clé primaire (station_id, bucket_hour)"""
    # GIVEN
    station_status_hourly_dao.bulk_upsert_hourly_stats(sample_hourly_stats)
    # Un autre enregistrement avec le même clé (station_id, bucket_hour)
    updated_record = StationStatusHourly(
        station_id="245557155",
        bucket_hour=datetime.fromisoformat("2026-11-01 01:00:00+00:00"),
        sample_count=24,
        avg_operational_capacity=5.0,
        avg_num_bikes_available=4.5,
        avg_num_docks_available=0.5,
        empty_duration_sec=0,
        full_duration_sec=1200,
        empty_events_cnt=0,
        full_events_cnt=2,
        reliability_score=70.0,
    )
    # WHEN
    upserted_count = station_status_hourly_dao.bulk_upsert_hourly_stats(
        [updated_record]
    )
    # THEN
    assert upserted_count == 1
    # Vérifier que les nouvelles valeurs sont mises à jour
    records = station_status_hourly_dao.get_hourly_stats(
        updated_record.station_id,
        datetime.fromisoformat("2026-11-01 01:00:00+00:00"),
        datetime.fromisoformat("2026-11-01 01:00:00+00:00"),
    )
    assert records
    assert records[0].sample_count == updated_record.sample_count
    assert records[0].full_events_cnt == updated_record.full_events_cnt
    assert records[0].reliability_score == updated_record.reliability_score


def test_bulk_upsert_hourly_stats_fail_none(station_status_hourly_dao):
    """L'insertion retourne 0 car l'argument est None ou vide"""
    assert station_status_hourly_dao.bulk_upsert_hourly_stats(None) == 0
    assert station_status_hourly_dao.bulk_upsert_hourly_stats([]) == 0


def test_bulk_upsert_hourly_stats_skip_none_record(
    station_status_hourly_dao, sample_hourly_stats
):
    """Les éléments None sont ignorés et les enregistrements valides sont insérés"""
    # GIVEN
    number_records = len(sample_hourly_stats)
    sample_hourly_stats.append(None)
    # WHEN
    upserted_count = station_status_hourly_dao.bulk_upsert_hourly_stats(
        sample_hourly_stats
    )
    # THEN
    assert upserted_count == number_records


def test_bulk_upsert_hourly_stats_fail_none_attr(
    station_status_hourly_dao, sample_hourly_stats
):
    """L'insertion est complètement annulée (retourne 0) si un champ NOT NULL est None"""
    # GIVEN
    sample_hourly_stats[0].sample_count = None
    # WHEN
    upserted_count = station_status_hourly_dao.bulk_upsert_hourly_stats(
        sample_hourly_stats
    )
    # THEN
    assert upserted_count == 0


# Tests de get_latest_hourly_status()
def test_get_latest_hourly_status_ok(station_status_hourly_dao, sample_hourly_stats):
    """Récupération du statut horaire le plus récent pour une station donnée"""
    # GIVEN
    station_status_hourly_dao.bulk_upsert_hourly_stats(sample_hourly_stats)
    station_id = "245557155"
    # WHEN
    latest = station_status_hourly_dao.get_latest_hourly_status(station_id)
    # THEN
    assert latest is not None
    assert latest.station_id == station_id
    assert latest.bucket_hour == datetime.fromisoformat("2026-11-01 02:00:00+00:00")
    assert latest.reliability_score == 90.0


def test_get_latest_hourly_status_fail_unknown_station(
    station_status_hourly_dao, sample_hourly_stats
):
    """Retourne None si l'identifiant de station n'existe pas"""
    # GIVEN
    station_status_hourly_dao.bulk_upsert_hourly_stats(sample_hourly_stats)
    # WHEN
    latest = station_status_hourly_dao.get_latest_hourly_status("unknown_id")
    # THEN
    assert latest is None


# Tests de get_hourly_stats()
def test_get_hourly_stats_ok(station_status_hourly_dao, sample_hourly_stats):
    """Récupère avec succès les statuts horaires sur une période définie"""
    # GIVEN
    station_status_hourly_dao.bulk_upsert_hourly_stats(sample_hourly_stats)
    station_id = "245557155"
    start_time = datetime.fromisoformat("2026-11-01 00:00:00+00:00")
    end_time = datetime.fromisoformat("2026-11-01 03:00:00+00:00")
    # WHEN
    records = station_status_hourly_dao.get_hourly_stats(
        station_id, start_time, end_time
    )
    # THEN
    assert len(records) == 2
    for r in records:
        assert r.station_id == station_id
        assert start_time <= r.bucket_hour <= end_time


def test_get_hourly_stats_wrong_id(station_status_hourly_dao, sample_hourly_stats):
    """Retourne une liste vide car l'identifiant de la station n'existe pas"""
    # GIVEN
    station_status_hourly_dao.bulk_upsert_hourly_stats(sample_hourly_stats)
    start_time = datetime.fromisoformat("2026-11-01 00:00:00+00:00")
    end_time = datetime.fromisoformat("2026-11-01 03:00:00+00:00")
    # WHEN
    records = station_status_hourly_dao.get_hourly_stats(
        "wrong_id", start_time, end_time
    )
    # THEN
    assert records == []


def test_get_hourly_stats_wrong_time(station_status_hourly_dao, sample_hourly_stats):
    """Retourne une liste vide car la période demandée n'a aucun enregistrement"""
    # GIVEN
    station_status_hourly_dao.bulk_upsert_hourly_stats(sample_hourly_stats)
    station_id = "245557155"
    start_time = datetime.fromisoformat("2026-12-01 00:00:00+00:00")
    end_time = datetime.fromisoformat("2026-12-01 03:00:00+00:00")
    # WHEN
    records = station_status_hourly_dao.get_hourly_stats(
        station_id, start_time, end_time
    )
    # THEN
    assert records == []


# Tests de aggregate_daily_stats()
def test_aggregate_daily_stats_ok(station_status_hourly_dao, sample_hourly_stats):
    """Agrégation journalière réussie sur une plage de dates"""
    # GIVEN
    station_status_hourly_dao.bulk_upsert_hourly_stats(sample_hourly_stats)
    station_id = "245557155"
    start_date = date(2026, 10, 31)
    end_date = date(2026, 11, 1)
    # WHEN
    daily_stats = station_status_hourly_dao.aggregate_daily_stats(
        station_id, start_date, end_date
    )
    # THEN
    assert len(daily_stats) == 2
    # Jour 1: 2026-10-31 (1 bucket à 23:00)
    day1 = daily_stats[0]
    assert day1["station_id"] == station_id
    assert day1["stat_date"] == date(2026, 10, 31)
    assert day1["sample_count"] == 24
    assert day1["avg_operational_capacity"] == 5
    assert day1["avg_num_bikes_available"] == 4  # ROUND(4.5)
    assert day1["avg_num_docks_available"] == 0  # ROUND(0.5)
    assert day1["empty_duration_sec"] == 0
    assert day1["full_duration_sec"] == 1200
    assert day1["empty_events_cnt"] == 0
    assert day1["full_events_cnt"] == 2
    assert day1["avg_reliability_score"] == 70
    # Jour 2: 2026-11-01 (2 buckets à 01:00 et 02:00)
    day2 = daily_stats[1]
    assert day2["station_id"] == station_id
    assert day2["stat_date"] == date(2026, 11, 1)
    assert day2["sample_count"] == 24  # 12 + 12
    assert day2["avg_operational_capacity"] == 5  # (5.0 + 5.0) / 2
    assert day2["avg_num_bikes_available"] == 3  # ROUND((2.5 + 3.0)/2 = 2.75) = 3
    assert day2["avg_num_docks_available"] == 2  # ROUND((2.5 + 2.0)/2 = 2.25) = 2
    assert day2["empty_duration_sec"] == 300  # 300 + 0
    assert day2["full_duration_sec"] == 600  # 0 + 600
    assert day2["empty_events_cnt"] == 1  # 1 + 0
    assert day2["full_events_cnt"] == 1  # 0 + 1
    assert day2["avg_reliability_score"] == 88  # ROUND((85.0 + 90.0)/2 = 87.5) = 88


def test_aggregate_daily_stats_wrong_id(station_status_hourly_dao, sample_hourly_stats):
    """Retourne une liste vide car l'identifiant n'est pas reconnu"""
    # GIVEN
    station_status_hourly_dao.bulk_upsert_hourly_stats(sample_hourly_stats)
    # WHEN
    daily_stats = station_status_hourly_dao.aggregate_daily_stats(
        "wrong_id", date(2026, 10, 31), date(2026, 11, 1)
    )
    # THEN
    assert daily_stats == []


def test_aggregate_daily_stats_wrong_time(
    station_status_hourly_dao, sample_hourly_stats
):
    """Retourne une liste vide car aucune donnée n'existe sur la période demandée"""
    # GIVEN
    station_status_hourly_dao.bulk_upsert_hourly_stats(sample_hourly_stats)
    # WHEN
    daily_stats = station_status_hourly_dao.aggregate_daily_stats(
        "245557155", date(2026, 12, 1), date(2026, 12, 2)
    )
    # THEN
    assert daily_stats == []

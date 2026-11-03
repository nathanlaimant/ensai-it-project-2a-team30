import os
from datetime import datetime

import pytest

from business_object.station_information import StationInformation
from business_object.station_state import StationState
from business_object.station_status import StationStatus
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from utils.db_connection import DbConnection
from utils.settings import Settings

stations = [
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
    StationInformation(
        station_id="245559919",
        name="Entzheim Gare",
        short_name="62003",
        lat=48.547222,
        lon=7.628056,
        address=None,
        is_virtual_station=False,
        station_area=None,
        contact_phone=None,
        capacity=10,
        is_charging_station=None,
    ),
    StationInformation(
        station_id="245564614",
        name="Geispolsheim Gare",
        short_name="62004",
        lat=48.521222,
        lon=7.684944,
        address=None,
        is_virtual_station=False,
        station_area=None,
        contact_phone=None,
        capacity=5,
        is_charging_station=None,
    ),
]

status = [
    StationStatus(
        station_id="245557155",
        num_bikes_available=2,
        num_bikes_disabled=None,
        num_docks_available=3,
        num_docks_disabled=None,
        operational_capacity=5,
        last_reported=datetime.fromisoformat("2026-11-01 01:04:24+00:00"),
        vehicle_types_available={"electric": 0, "mechanical": 2},
        vehicle_docks_available=None,
        station_state=StationState.FUNCTIONAL,
    ),
    StationStatus(
        station_id="245557947",
        num_bikes_available=2,
        num_bikes_disabled=None,
        num_docks_available=8,
        num_docks_disabled=None,
        operational_capacity=10,
        last_reported=datetime.fromisoformat("2026-11-01 01:04:24+00:00"),
        vehicle_types_available={"electric": 0, "mechanical": 2},
        vehicle_docks_available=None,
        station_state=StationState.FUNCTIONAL,
    ),
    StationStatus(
        station_id="245559919",
        num_bikes_available=3,
        num_bikes_disabled=None,
        num_docks_available=7,
        num_docks_disabled=None,
        operational_capacity=10,
        last_reported=datetime.fromisoformat("2026-11-01 01:04:24+00:00"),
        vehicle_types_available={"electric": 0, "mechanical": 3},
        vehicle_docks_available=None,
        station_state=StationState.FUNCTIONAL,
    ),
    StationStatus(
        station_id="245564614",
        num_bikes_available=5,
        num_bikes_disabled=None,
        num_docks_available=0,
        num_docks_disabled=None,
        operational_capacity=5,
        last_reported=datetime.fromisoformat("2026-11-01 01:04:24+00:00"),
        vehicle_types_available={"electric": 0, "mechanical": 5},
        vehicle_docks_available=None,
        station_state=StationState.FULL,
    ),
]


@pytest.fixture(scope="session")
def db_connection():
    """Provides a connection pool to the test database schema."""
    settings = Settings(
        postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
        postgres_port=int(os.getenv("POSTGRES_PORT", 5432)),
        postgres_database=os.getenv("POSTGRES_DB", "defaultdb"),
        postgres_user=os.getenv("POSTGRES_USER", "postgres"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        postgres_schema=os.getenv("SCHEMA", "project_test_dao"),
        system_information_feed_url="http://mock",
        station_information_feed_url="http://mock",
        station_status_feed_url="http://mock",
    )
    return DbConnection(settings)


@pytest.fixture(autouse=True)
def setup_test_environment(db_connection):
    """
    Cleans up and seeds required parent stations before tests run.
    """
    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM station_status;")
                cur.execute("DELETE FROM station_information;")
                station_dao = StationDAO(db_connection)
                for st in stations:
                    station_dao.upsert_station_info(st)


@pytest.fixture
def station_status_dao(db_connection):
    return StationStatusDAO(db_connection)


# Tests de bulk_insert_status()
def test_bulk_insert_status_ok(station_status_dao):
    """Insertions du nouveau statut des stations réussies"""

    # GIVEN
    number_status = len(statuses)

    # WHEN
    updates_made = station_status_dao.bulk_insert_status(status)

    # THEN
    assert updates_made == number_status


def test_bulk_insert_status_fail(station_status_dao):
    """Insertion du nouveau statut des stations incomplète car toutes les stations
    à mettre à jour n'ont pas été intégrées en argument de la fonction"""

    # GIVEN
    number_status = len(statuses)

    # WHEN
    updates_made = station_status_dao.bulk_insert_status(status[:1])

    # THEN
    assert updates_made != number_status


# Tests de get_latest_status()
def test_get_latest_status_ok(station_status_dao):
    """Mise à jour de la station réussie"""

    # GIVEN
    station_status_dao.bulk_insert_status(status)
    id_station = status[1].station_id

    # WHEN
    result = station_status_dao.get_latest_status(id_station)

    # THEN
    assert result is not None
    assert result.station_id == id_station


def test_get_latest_status_fail(station_status_dao):
    """Mise à jour de la station impossible car l'identifiant n'existe pas"""

    # GIVEN
    id_station = "fakeid"

    # WHEN
    result = station_status_dao.get_latest_status(id_station)

    # THEN
    assert result is None


# Tests de get_status_history()
def test_get_status_history_ok(station_status_dao):
    """Nous réussissons à obtenir l'historique du statut d'une station sur une période donnée"""

    # GIVEN
    station_status_dao.bulk_insert_status(status)
    target_station_id = status[2].station_id
    start_time = datetime.fromisoformat("2026-11-01 00:00:00+00:00")
    end_time = datetime.fromisoformat("2026-11-01 02:00:00+00:00")

    # WHEN
    status_history = station_status_dao.get_status_history(
        target_station_id, start_time, end_time
    )

    # THEN
    assert status_history
    for s in status_history:
        assert s.station_id == target_station_id
        assert start_time <= s.last_reported <= end_time


def test_get_status_history_fail(station_status_dao):
    """Nous échouons à obtenir l'historique du statut d'une station car son identifiant n'est
    pas reconnu"""

    # GIVEN
    station_id = "fakeid"
    start_time = datetime.fromisoformat("2026-11-01 00:00:00+00:00")
    end_time = datetime.fromisoformat("2026-11-01 02:00:00+00:00")

    # WHEN
    status_history = station_status_dao.get_status_history(
        station_id, start_time, end_time
    )

    # THEN
    assert status_history == []

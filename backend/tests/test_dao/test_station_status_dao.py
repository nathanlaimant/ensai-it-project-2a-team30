from datetime import datetime
from pathlib import Path

import pytest

from business_object.station_information import StationInformation
from business_object.station_state import StationState
from business_object.station_status import StationStatus
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
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
                cur.execute("DELETE FROM station_status;")
                cur.execute("DELETE FROM station_information;")

    station_dao = StationDAO(db_connection)
    for st in initial_stations:
        station_dao.upsert_station_info(st)

    yield initial_stations

    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM station_status;")
                cur.execute("DELETE FROM station_information;")


@pytest.fixture(autouse=True)
def setup_test_environment(db_connection, initiate_stations):
    """
    Nettoie uniquement la table station_status avant chaque test.
    """
    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM station_status;")


@pytest.fixture
def sample_statuses():
    """Génère une liste isolée d'objets StationStatus pour chaque test."""
    return [
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
            station_id="245557155",
            num_bikes_available=3,
            num_bikes_disabled=None,
            num_docks_available=7,
            num_docks_disabled=None,
            operational_capacity=10,
            last_reported=datetime.fromisoformat("2026-11-01 00:34:24+00:00"),
            vehicle_types_available={"electric": 0, "mechanical": 3},
            vehicle_docks_available=None,
            station_state=StationState.FUNCTIONAL,
        ),
        StationStatus(
            station_id="245557155",
            num_bikes_available=5,
            num_bikes_disabled=None,
            num_docks_available=0,
            num_docks_disabled=None,
            operational_capacity=5,
            last_reported=datetime.fromisoformat("2026-11-01 00:04:24+00:00"),
            vehicle_types_available={"electric": 0, "mechanical": 5},
            vehicle_docks_available=None,
            station_state=StationState.FULL,
        ),
    ]


@pytest.fixture
def station_status_dao(db_connection):
    return StationStatusDAO(db_connection)


# Tests de bulk_insert_status()
def test_bulk_insert_status_ok(station_status_dao, sample_statuses):
    """Insertions du nouveau statut des stations réussies"""
    # GIVEN
    number_status = len(sample_statuses)
    # WHEN
    updates_made = station_status_dao.bulk_insert_status(sample_statuses)
    # THEN
    assert updates_made == number_status


def test_bulk_insert_status_fail_none(station_status_dao):
    """Insertion retourne 0 car l'entrée est None"""
    # GIVEN
    none_input = None
    # WHEN
    updates_made = station_status_dao.bulk_insert_status(none_input)
    # THEN
    assert updates_made == 0


def test_bulk_insert_status_fail_none_record(station_status_dao, sample_statuses):
    """
    Insertion retourne n-1 car l'un des enregistrements est None,
    cet enregistrement est ignoré et les autres sont insérés
    """
    # GIVEN
    sample_statuses.append(None)
    number_status = len(sample_statuses)
    # WHEN
    updates_made = station_status_dao.bulk_insert_status(sample_statuses)
    # THEN
    assert updates_made == number_status - 1


def test_bulk_insert_status_fail_none_attr(station_status_dao, sample_statuses):
    """
    Insertion retourne 0 car l'un des attributs d'un enregistrement est None,
    l'insertion est completement annulée
    """
    # GIVEN
    sample_statuses[0].operational_capacity = None
    # WHEN
    updates_made = station_status_dao.bulk_insert_status(sample_statuses)
    # THEN
    assert updates_made == 0


# Tests de get_latest_status()
def test_get_latest_status_ok(station_status_dao, sample_statuses):
    """
    Il y a 3 statuts à 3 moments différents pour une station.
    Requête réussie pour obtenir le dernier.
    """
    # GIVEN
    station_status_dao.bulk_insert_status(sample_statuses)
    id_station = sample_statuses[0].station_id
    # WHEN
    result = station_status_dao.get_latest_status(id_station)
    # THEN
    assert result is not None
    assert result.station_id == id_station
    assert result.last_reported == sample_statuses[0].last_reported


def test_get_latest_status_fail(station_status_dao, sample_statuses):
    """Requête retourne None car l'identifiant n'existe pas"""
    # GIVEN
    station_status_dao.bulk_insert_status(sample_statuses)
    id_station = "fakeid"
    # WHEN
    result = station_status_dao.get_latest_status(id_station)
    # THEN
    assert result is None


# Tests de get_latest_statuses()
def test_get_latest_statuses_ok(station_status_dao, sample_statuses):
    """Récupère en une requête le dernier statut de chaque station demandée"""
    # GIVEN
    station_status_dao.bulk_insert_status(sample_statuses)
    station_ids = ["245557155", "245557947", "fakeid"]
    # WHEN
    results = station_status_dao.get_latest_statuses(station_ids)
    # THEN
    assert len(results) == 2
    assert "fakeid" not in results
    assert results["245557155"].last_reported == sample_statuses[0].last_reported
    assert results["245557947"].last_reported == sample_statuses[1].last_reported


def test_get_latest_statuses_empty_input(station_status_dao):
    """Retourne {} si la liste d'identifiants est vide"""
    # WHEN
    results = station_status_dao.get_latest_statuses([])
    # THEN
    assert results == {}


def test_get_latest_statuses_unknown_ids(station_status_dao, sample_statuses):
    """Retourne {} si aucun identifiant n'existe"""
    # GIVEN
    station_status_dao.bulk_insert_status(sample_statuses)
    # WHEN
    results = station_status_dao.get_latest_statuses(["fakeid1", "fakeid2"])
    # THEN
    assert results == {}


# Tests de get_one_station_history()
def test_get_one_station_history_ok(station_status_dao, sample_statuses):
    """Requête réussie pour obtenir l'historique du statut d'une station sur une période donnée"""
    # GIVEN
    station_status_dao.bulk_insert_status(sample_statuses)
    target_station_id = sample_statuses[0].station_id
    start_time = datetime.fromisoformat("2026-11-01 00:24:24+00:00")
    end_time = datetime.fromisoformat("2026-11-01 00:44:24+00:00")
    # WHEN
    status_history = station_status_dao.get_one_station_history(
        target_station_id, start_time, end_time
    )
    # THEN
    assert status_history
    assert len(status_history) == 1
    assert status_history[0].station_id == target_station_id
    assert start_time <= status_history[0].last_reported <= end_time


def test_get_status_history_fail_fakeid(station_status_dao, sample_statuses):
    """Requête retourne [] car l'identifiant n'existe pas"""
    # GIVEN
    station_status_dao.bulk_insert_status(sample_statuses)
    station_id = "fakeid"
    start_time = datetime.fromisoformat("2026-11-01 00:24:24+00:00")
    end_time = datetime.fromisoformat("2026-11-01 00:44:24+00:00")
    # WHEN
    status_history = station_status_dao.get_one_station_history(
        station_id, start_time, end_time
    )
    # THEN
    assert status_history == []


def test_get_status_history_fail_nothing(station_status_dao, sample_statuses):
    """Requête retourne [] car il n'y a pas de statut pour la station dans la période donnée"""
    # GIVEN
    station_status_dao.bulk_insert_status(sample_statuses)
    target_station_id = sample_statuses[0].station_id
    start_time = datetime.fromisoformat("2026-11-02 00:24:24+00:00")
    end_time = datetime.fromisoformat("2026-11-02 00:44:24+00:00")
    # WHEN
    status_history = station_status_dao.get_one_station_history(
        target_station_id, start_time, end_time
    )
    # THEN
    assert status_history == []


# Tests de get_all_station_history()
def test_get_all_station_history_ok(station_status_dao, sample_statuses):
    """Requête réussie pour obtenir l'historique du statut de toutes les stations sur une période donnée"""
    # GIVEN
    station_status_dao.bulk_insert_status(sample_statuses)
    start_time = datetime.fromisoformat("2026-11-01 00:24:24+00:00")
    end_time = datetime.fromisoformat("2026-11-01 01:14:24+00:00")
    # WHEN
    status_history = station_status_dao.get_all_station_history(start_time, end_time)
    # THEN
    assert status_history
    assert len(status_history) == 2
    for statuses in status_history.values():
        for status in statuses:
            assert start_time <= status.last_reported <= end_time


def test_get_all_station_history_fail_nothing(station_status_dao, sample_statuses):
    """Requête retourne {} car il n'y a pas de statut pour les stations dans la période donnée"""
    # GIVEN
    station_status_dao.bulk_insert_status(sample_statuses)
    start_time = datetime.fromisoformat("2026-11-02 00:24:24+00:00")
    end_time = datetime.fromisoformat("2026-11-02 00:44:24+00:00")
    # WHEN
    status_history = station_status_dao.get_all_station_history(start_time, end_time)
    # THEN
    assert status_history == {}

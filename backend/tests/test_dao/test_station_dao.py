from pathlib import Path

import pytest

from business_object.station_information import StationInformation
from dao.station_dao import StationDAO
from utils.db_connection import DbConnection
from utils.settings import Settings

test_env_path = Path(__file__).resolve().parents[1] / ".test_env"


@pytest.fixture(scope="session")
def db_connection():
    """Provides a connection pool to the test database schema."""
    settings = Settings(_env_file=".test_env")
    return DbConnection(settings)


@pytest.fixture
def station_dao(db_connection):
    return StationDAO(db_connection)


# Test de upsert_station_info()


def test_upsert_station_info_ok(station_dao):
    """L'importation de l'API externe avec la liste des stations a réussi"""

    # GIVEN
    external_data = StationInformation(
            station_id="19179944124",
            name="Hôpital Mondor",
            short_name="40001",
            lat=48.798922410229,
            lon=2.4537451531298,
            capacity=28,
        )

    # WHEN
    added = station_dao.upsert_station_info(external_data)

    # THEN
    assert added


# Tests de get_by_id()


def test_get_by_id_ok(station_dao):
    """Recherche d'une station par son identifiant réussie"""

    # GIVEN
    id_station = "251039991"

    # WHEN
    station = station_dao.get_by_id(id_station)

    # THEN
    assert isinstance(station, StationInformation)


def test_get_by_id_fail(station_dao):
    """Recherche d'une station par son identifiant impossible car l'identifiant n'existe pas"""

    # GIVEN
    id_station = "fakeid"

    # WHEN
    station = station_dao.get_by_id(id_station)

    # THEN
    assert station is None


# Tests de get_nearby()


def test_get_nearby_ok(station_dao):
    """Recheche de stations proches réussie"""

    # GIVEN
    lat, lon, radius_meter = 48.865983, 2.275725, 20

    # WHEN
    stations = station_dao.get_nearby(lat, lon, radius_meter)

    # THEN
    assert stations is not None


def test_get_nearby_fail(station_dao):
    """Recheche de stations proches impossible car les coordonnées n'existent pas"""

    # GIVEN
    lat, lon, radius_meter = 5425.65, -65.09, 20

    # WHEN
    stations = station_dao.get_nearby(lat, lon, radius_meter)

    # THEN
    assert stations is None


# Tests de list_stations()


def test_list_stations_ok(station_dao):
    """Nous arrivons à obtenir la liste de l'ensemble des stations correspondant à la
    recherche effectuée"""

    # GIVEN
    a_name = "Toudouze"

    # WHEN
    stations = station_dao.list_stations(name=a_name)

    # THEN
    assert stations is not None
    for s in stations:
        assert isinstance(s, StationInformation)


def test_list_stations_fail(station_dao):
    """Nous n'arrivons pas à obtenir la liste de l'ensemble des stations correspondant à la
    recherche effectuée car le nom n'existe pas"""

    # GIVEN
    a_name = "afakenameverylongthatistoolong"

    # WHEN
    stations = station_dao.list_stations(name=a_name)

    # THEN
    assert stations is None

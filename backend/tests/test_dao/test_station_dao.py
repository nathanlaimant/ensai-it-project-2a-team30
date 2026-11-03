from pathlib import Path

import psycopg2
import pytest

from business_object.station_information import StationInformation
from dao.station_dao import StationDao
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
    return StationDao(db_connection)


# Test de upsert_station_info()


def test_upsert_station_info_ok():
    """L'importation de l'API externe avec la liste des stations a réussi"""

    # GIVEN
    external_data = [
        StationInformation(
            station_id="19179944124",
            name="Hôpital Mondor",
            short_name="40001",
            lat=48.798922410229,
            lon=2.4537451531298,
            capacity=28,
        )
    ]

    # WHEN
    local_data = StationDao().upsert_station_info(external_data)

    # THEN
    assert local_data


def test_upsert_station_info_fail():
    """L'importation de l'API externe à la liste des stations échoue car un des attributs de la
    classe StationInformation est incorrect"""

    # GIVEN
    station = StationInformation(
        station_id="74a3f9a1-70b0-4d9a-a1d1-bbb5c6948840",
        name="id_old844604G20081106092237",
        lat=48.8322843827352,
        lon=2.32105516137791,
        is_virtual_station=True,
        capacity="3",
    )

    # WHEN / THEN
    with pytest.raises(psycopg2.Error):
        StationDao().upsert_station_info(station)


# Tests de get_by_id()


def test_get_by_id_ok():
    """Recherche d'une station par son identifiant réussie"""

    # GIVEN
    id_station = "16bbf68d-685a-4799-9bba-8915f10700e0"

    # WHEN
    station = StationDao().get_by_id(id_station)

    # THEN
    assert isinstance(station, StationInformation)


def test_get_by_id_fail():
    """Recherche d'une station par son identifiant impossible car l'identifiant n'existe pas"""

    # GIVEN
    id_station = "fakeid"

    # WHEN
    station = StationDao().get_by_id(id_station)

    # THEN
    assert station is None


# Tests de get_nearby()


def test_get_nearby_ok():
    """Recheche de stations proches réussie"""

    # GIVEN
    lat, lon, radius_meter = 48.8727256662692, 2.35437813765038, 20

    # WHEN
    stations = StationDao().get_nearby(lat, lon, radius_meter)

    # THEN
    assert stations is not None


def test_get_nearby_fail():
    """Recheche de stations proches impossible car les coordonnées n'existent pas"""

    # GIVEN
    lat, lon, radius_meter = 5425.65, -65.09, 20

    # WHEN
    stations = StationDao().get_nearby(lat, lon, radius_meter)

    # THEN
    assert stations is None


# Tests de list_stations()


def test_list_stations_ok():
    """Nous arrivons à obtenir la liste de l'ensemble des stations correspondant à la
    recherche effectuée"""

    # GIVEN
    a_name = "Toudouze - Clauzel"

    # WHEN
    stations = StationDao().list_stations(name=a_name)

    # THEN
    assert stations is not None
    for s in stations:
        assert isinstance(s, StationInformation)


def test_list_stations_fail():
    """Nous n'arrivons pas à obtenir la liste de l'ensemble des stations correspondant à la
    recherche effectuée car le nom n'existe pas"""

    # GIVEN
    a_name = "afakenameverylongthatistoolong"

    # WHEN
    stations = StationDao().list_stations(name=a_name)

    # THEN
    assert stations is None

import os
from unittest.mock import patch

import psycopg3
import pytest
from utils.reset_database import ResetDatabase

from business_object.station_information import StationInformation
from dao.station_dao import StationDao

stations_list = [
    StationInformation(
        station_id="16bbf68d-685a-4799-9bba-8915f10700e0",
        name="id_38206",
        lat=48.8727256662692,
        lon=2.35437813765038,
        is_virtual_station=True,
        capacity=3
    ),
    StationInformation(
        station_id="b42cb6d7-0558-4589-ad71-63e374fdb784",
        name="id_34235",
        lat=48.8266089252496,
        lon=2.33467058582095,
        is_virtual_station=True,
        capacity=3
    ),
    StationInformation(
        station_id="5770705c-cbb1-4baa-a1ca-eb40540b2f40",
        name="17 RUE DU VIEUX COLOMBIER",
        lat=48.851759,
        lon=2.3306,
        is_virtual_station=True,
        capacity=3
    ),
    StationInformation(
        station_id="74a3f9a1-70b0-4d9a-a1d1-bbb5c6948840",
        name="id_old844604G20081106092237",
        lat=48.8322843827352,
        lon=2.32105516137791,
        is_virtual_station=True,
        capacity=3
    )
]


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation de la base de données pour les tests"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


# Test de upsert_station_info()

def test_upsert_station_info_ok():
    """L'importation de l'API externe avec la liste des stations a réussi"""

    # GIVEN
    local_data = [stations_list[0]]
    external_data = [stations_list[1]]

    # WHEN
    local_data = StationDao().upsert_station_info(external_data)

    # THEN
    assert (local_data == external_data) is True


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
        capacity="3"
    )

    # WHEN / THEN
    with pytest.raises(psycopg3.Error):
        StationDao().upsert_station_info(station)


# Tests de get_by_id()

def test_get_by_id_ok():
    """Recherche d'une station par son identifiant réussie"""

    # GIVEN
    id_station = "16bbf68d-685a-4799-9bba-8915f10700e0"

    # WHEN
    station = StationDao().get_by_id(id_station)

    # THEN
    assert station is not None


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
    name = "id_34235"

    # WHEN
    stations = StationDao().list_stations({"name": name})

    # THEN
    assert stations is not None


def test_list_stations_fail():
    """Nous n'arrivons pas à obtenir la liste de l'ensemble des stations correspondant à la
    recherche effectuée car le nom n'existe pas"""

    # GIVEN
    name = "afakenameverylongthatistoolong"

    # WHEN
    stations = StationDao().list_stations({"name": name})

    # THEN
    assert stations is None

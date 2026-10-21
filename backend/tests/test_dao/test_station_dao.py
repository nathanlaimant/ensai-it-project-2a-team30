import os
from unittest.mock import patch

import psycopg3
import pytest
from utils.reset_database import ResetDatabase

from business_object.station_information import StationInformation
from dao.station_dao import StationDao

stations_list = [
    StationInformation(
        station_id="213688169",
        name="Benjamin Godard - Victor Hugo",
        short_name="16107",
        lat=48.865983,
        lon=2.275725,
        capacity=35
    ),
    StationInformation(
        station_id="19179944124",
        name="Hôpital Mondor",
        short_name="40001",
        lat=48.798922410229,
        lon=2.4537451531298,
        capacity=28
    ),
    StationInformation(
        station_id="18795078746",
        name="Charcot - Benfleet",
        short_name="32304",
        lat=48.878370277021,
        lon=2.440523876268,
        capacity=28
    ),
    StationInformation(
        station_id="36255",
        name="Toudouze - Clauzel",
        short_name="9020",
        lat=48.87929591733507,
        lon=2.3373600840568547,
        capacity=21
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
    external_data = [stations_list[1]]

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
    name = "Toudouze - Clauzel"

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

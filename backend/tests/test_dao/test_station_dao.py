import os
from unittest.mock import patch

import pytest
from utils.reset_database import ResetDatabase

from business_object.station_information import StationInformation
from dao.station_dao import StationDao

stations_list = [
    StationInformation(
        station_id="id1",
        name="name1",
        short_name="n1",
        lat=4.0,
        lon=0.9,
        address="address1",
        is_virtual_station=True,
        station_area={
            type: "MultiPolygon",
            "coordinates": [
                [
                    [
                        [
                            11.51,
                            54.65
                        ],
                        [
                            54.87,
                            86.21
                        ],
                        [
                            65.21,
                            66.02
                        ]
                    ]
                ]
            ]
        },
        contact_phone="phone1",
        capacity=17,
        is_charging_station=False
    ),
    StationInformation(
        station_id="id1",
        name="name1",
        short_name="n1",
        lat=4.0,
        lon=0.9,
        address="address2",
        is_virtual_station=True,
        station_area={
            type: "MultiPolygon",
            "coordinates": [
                [
                    [
                        [
                            11.51,
                            54.65
                        ],
                        [
                            54.87,
                            86.21
                        ],
                        [
                            65.61,
                            66.02
                        ]
                    ]
                ]
            ]
        },
        contact_phone="phone1",
        capacity=17,
        is_charging_station=False
    ),
    StationInformation(),
    StationInformation()
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
    local_data = StationDao(external_data)

    # THEN
    assert (local_data == external_data) is True



# Tests de get_by_id()

def test_get_by_id_ok():
    """Recherche d'une station par son identifiant réussie"""

    # GIVEN
    id_station = "anid"

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
    lat, lon, radius_meter = 25.65, -65.09, 20

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
    name = "nam"

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

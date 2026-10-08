import os
from unittest.mock import patch, MagicMock

import psycopg2
import pytest
from utils.reset_database import ResetDatabase

from business_object.user import User
from business_object.station_information import StationInformation
from dao.favorite_station_dao import FavoriteStationDAO

user = User()

stations_list = [
    StationInformation(),
    StationInformation(),
    StationInformation()
]

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation de la base de données pour les tests"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


# Tests de add_favorite()

def test_add_favorite_possible():
    """Réussite de l'ajout de la station à la liste des favoris"""

    # GIVEN
    user_id, station_id = user.user_id, stations_list[1].station_id
    UserDAO().get_by_id(user_id) = MagicMock(return_value=user)
    StationDAO().get_by_id(station_id) = MagicMock(return_value=station_list[1])

    # WHEN
    added = FavoriteStationDAO().add_favorite(user_id, station_id)

    # THEN
    assert added


def test_add_favorite_already_favorite():
    """La station est déjà présente dans la liste des favoris"""

    # GIVEN
    user_id, station_id = user.user_id, stations_list[0].station_id
    UserDAO().get_by_id(user_id) = MagicMock(return_value=user)
    StationDAO().get_by_id(station_id) = MagicMock(return_value=stations_list[0])

    # WHEN
    added = FavoriteStationDAO().add_favorite(user_id, station_id)

    # THEN
    assert not added


def test_add_favorite_station_non_existing():
    """Impossibilité d'ajouter la station à la liste des favoris car son identifiant
    n'est pas reconnu"""

    # GIVEN
    user_id, station_id = user.user_id, "fakeid"
    UserDAO().get_by_id(user_id) = MagicMock(return_value=user)
    StationDAO().get_by_id(station_id) = MagicMock(return_value=None)

    # WHEN
    added = FavoriteStationDAO().add_favorite(user_id, station_id)
    
    # THEN
    assert not added


# Tests de list_by_user()

def test_list_by_user_ok():
    """Nous réussissons à obtenir la liste des stations favorites d'un utilisateur
    grâce à son identifiant"""

    # GIVEN
    user_id = user.user_id
    UserDAO().get_by_id(user_id) = MagicMock(return_value=user)

    # WHEN
    list = FavoriteStationDAO().list_by_user(user_id)

    # THEN
    for s in list:
        assert isinstance(s, StationInformation)
    assert len(list) == 2


def test_list_by_user_wrong_id():
    """Impossibilité d'obtenir la liste des stations favorites d'un utilisateur
    car son identifiant n'est pas reconnu"""

    # GIVEN
    user_id = 756576879
    UserDAO().get_by_id(user_id) = MagicMock(return_value=None)

    # WHEN
    list = FavoriteStationDAO().list_by_user(user_id)

    # THEN
    assert list is None


# Tests de count_favorites()

def test_count_favorite_one_station():
    """Nous arrivons à savoir combien d'utilisateurs ont mis la station dans leur
    liste des stations favorites"""

    # GIVEN
    station_id = [stations_list[0].station_id]
    StationDAO().get_by_id(station_id[0]) = MagicMock(return_value=stations_list[0])

    # WHEN
    count = FavoriteStationDAO().count_favorites(station_id)

    # THEN
    assert isinstance(count, dict)
    assert count[station_id] == 2


def test_count_favorite_multiple_stations():
    """Nous arrivons à savoir combien d'utilisateurs ont mis les stations dans leur
    liste des stations favorites"""

    # GIVEN
    station_ids = [
        stations_list[0].station_id,
        stations_list[1].station_id,
        stations_list[2].station_id
    ]
    for i in range(len(station_ids)):
        StationDAO().get_by_id(station_ids[i]) = MagicMock(
            return_value=stations_list[i]
        )

    # WHEN
    counts = FavoriteStationDAO().count_favorites(station_id)

    # THEN
    assert isinstance(counts, dict) and len(counts) == 3
    assert (counts[station_ids[0]] == 2 and counts[station_ids[1]] == 0 and counts[station_ids[2]] == 3)


def test_count_favorite_wrong_id():
    """Nous échouns à obtenir le nombre d'utilisateurs qui ont mis les stations dans
    leur liste des stations favorites car un des identifiants n'est pas reconnu"""

    # GIVEN
    station_ids = [
        stations_list[0].station_id,
        "wrongid",
        stations_list[2].station_id
    ]
    StationDAO().get_by_id(station_ids[0]) = MagicMock(return_value=stations_list[0])
    StationDAO().get_by_id(station_ids[1]) = MagicMock(return_value=None)
    StationDAO().get_by_id(station_ids[2]) = MagicMock(return_value=stations_list[2])

    # WHEN
    counts = FavoriteStationDAO().count_favorites(station_ids)

    # THEN
    assert counts is None

# Tests de remove_favorite()

def test_remove_favorite_ok():
    """Nous réussissons à retirer la station de la liste des stations favorites
    de l'utilisateur donné"""

    # GIVEN
    user_id, station_id = user.user_id, stations_list[0].station_id
    UserDAO().get_by_id(user_id) = MagicMock(return_value=user)
    StationDAO().get_by_id(station_id) = MagicMock(return_value=stations_list[0])

    # WHEN
    removed = FavoriteStationDAO().remove_favorite(user_id, station_id)

    # THEN
    assert removed


def test_remove_favorite_not_favorite():
    """Nous ne pouvons pas retirer la station de la liste des favoris de l'utilisateur
    car celle-ci n'en fait pas partie"""

    # GIVEN
    user_id, station_id = user.user_id, stations_list[1].station_id
    UserDAO().get_by_id(user_id) = MagicMock(return_value=user)
    StationDAO().get_by_id(station_id) = MagicMock(return_value=station_list[1])

    # WHEN
    removed = FavoriteStationDAO().remove_favorite(user_id, station_id)

    # THEN
    assert not removed


def test_remove_favorite_user_non_existing():
    """Nous ne pouvons pas retirer la station de la liste des favoris de l'utilisateur
    car l'identifiant de ce dernier n'est pas reconnu"""

    # GIVEN
    user_id, station_id = 5545476868, stations_list[1].station_id
    UserDAO().get_by_id(user_id) = MagicMock(return_value=None)
    StationDAO().get_by_id(station_id) = MagicMock(return_value=station_list[1])

    # WHEN
    removed = FavoriteStationDAO().remove_favorite(user_id, station_id)

    # THEN
    assert not removed

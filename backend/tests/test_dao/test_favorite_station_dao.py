from unittest.mock import MagicMock

import pytest

from business_object.station_information import StationInformation
from dao.favorite_station_dao import FavoriteStationDAO


@pytest.fixture
def favorite_station_dao():
    """Prépare un DAO et un curseur simulé pour les tests."""
    db_connection = MagicMock()
    connection = MagicMock()
    cursor = MagicMock()
    db_connection.get_connection.return_value.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor
    return FavoriteStationDAO(db_connection), cursor


# Tests de add_favorite()

def test_add_favorite_ok(favorite_station_dao):
    """Réussite de l'ajout de la station à la liste des favoris"""

    # GIVEN
    dao, cursor = favorite_station_dao
    user_id, station_id = 1, "station-1"
    cursor.fetchone.return_value = {"station_id": station_id}

    # WHEN
    added = dao.add_favorite(user_id, station_id)

    # THEN
    assert added


def test_add_favorite_already_favorite(favorite_station_dao):
    """La station est déjà présente dans la liste des favoris"""

    # GIVEN
    dao, cursor = favorite_station_dao
    user_id, station_id = 1, "station-1"
    cursor.fetchone.return_value = None

    # WHEN
    added = dao.add_favorite(user_id, station_id)

    # THEN
    assert not added



# Tests de count_favorites()

def test_count_favorites_multiple_stations(favorite_station_dao):
    """Nous arrivons à savoir combien d'utilisateurs ont mis les stations dans leur
    liste des stations favorites"""

    # GIVEN
    dao, cursor = favorite_station_dao
    station_ids = ["station-1", "station-2", "station-3"]
    cursor.fetchall.return_value = [
        {"station_id": "station-1", "favorite_count": 2},
        {"station_id": "station-2", "favorite_count": 0},
        {"station_id": "station-3", "favorite_count": 3},
    ]

    # WHEN
    counts = dao.count_favorites(station_ids)

    # THEN
    assert isinstance(counts, dict) and len(counts) == 3
    assert counts[station_ids[0]] == 2
    assert counts[station_ids[1]] == 0
    assert counts[station_ids[2]] == 3


# Tests de remove_favorite()

def test_remove_favorite_ok(favorite_station_dao):
    """Nous réussissons à retirer la station de la liste des stations favorites
    de l'utilisateur donné"""

    # GIVEN
    dao, cursor = favorite_station_dao
    user_id, station_id = 1, "station-1"
    cursor.fetchone.return_value = {"station_id": station_id}

    # WHEN
    removed = dao.remove_favorite(user_id, station_id)

    # THEN
    assert removed


def test_remove_favorite_not_favorite(favorite_station_dao):
    """Nous ne pouvons pas retirer la station de la liste des favoris de l'utilisateur
    car celle-ci n'en fait pas partie"""

    # GIVEN
    dao, cursor = favorite_station_dao
    user_id, station_id = 1, "station-1"
    cursor.fetchone.return_value = None

    # WHEN
    removed = dao.remove_favorite(user_id, station_id)

    # THEN
    assert not removed



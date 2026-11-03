from pathlib import Path

import pytest

from dao.favorite_station_dao import FavoriteStationDAO
from utils.db_connection import DbConnection
from utils.settings import Settings

test_env_path = Path(__file__).resolve().parents[1] / ".test_env"


@pytest.fixture(scope="session")
def db_connection():
    """Provides a connection pool to the test database schema."""
    settings = Settings(_env_file=".test_env")
    return DbConnection(settings)


@pytest.fixture
def favorite_station_dao(db_connection):
    return FavoriteStationDAO(db_connection)


def test_add_favorite_ok(favorite_station_dao):
    # GIVEN
    station_id = "251039991"
    user_id = 24

    # WHEN
    added = favorite_station_dao.add_favorite(user_id, station_id)

    # THEN
    assert added


def test_add_favorite_for_unknown_user(favorite_station_dao):
    # GIVEN
    station_id = "19179944124"
    user_id = 2

    # WHEN
    fav = favorite_station_dao.add_favorite(user_id, station_id)

    # THEN
    assert fav is False

def test_add_favorite_for_unknown_station(favorite_station_dao):
    # GIVEN
    station_id = "1954223"
    user_id = 21

    # WHEN
    fav = favorite_station_dao.add_favorite(user_id, station_id)

    # THEN
    assert fav is False

def test_list_favorites(favorite_station_dao):
    # GIVEN
    user_id = 21
    station_id = "19179944124"
    favorite_station_dao.add_favorite(user_id, station_id)

    # WHEN
    favorites = favorite_station_dao.list_favorites({"user_id": user_id})

    # THEN
    assert len(favorites) > 0


def test_count_favorites_from_database(favorite_station_dao):
    # GIVEN
    station_id = "19179944124"

    # WHEN / THEN
    assert favorite_station_dao.count_favorites([station_id]) == {station_id: 1}


def test_remove_favorite(favorite_station_dao):
    # GIVEN
    station_id = "19179944124"
    user_id = 22
    fav = favorite_station_dao.add_favorite(user_id, station_id)

    # WHEN
    fav = favorite_station_dao.remove_favorite(user_id, station_id)

    # THEN
    assert fav is True
 

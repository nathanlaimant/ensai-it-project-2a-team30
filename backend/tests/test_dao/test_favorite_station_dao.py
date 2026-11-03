from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest

from business_object.station_information import StationInformation
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
def favorite_dao(db_connection):
    return FavoriteStationDAO(db_connection)


def test_add_favorite_and_reject_duplicate(favorite_station_dao):
    favorite_dao, _, user_id, station_id = favorite_dao_context

    assert favorite_dao.add_favorite(user_id, station_id)
    assert not favorite_dao.add_favorite(user_id, station_id)


def test_add_favorite_for_unknown_user(favorite_station_dao):
    favorite_dao, _, user_id, station_id = favorite_dao_context

    assert not favorite_dao.add_favorite(user_id + 10_000_000, station_id)


def test_add_favorite_for_unknown_station(favorite_station_dao):
    favorite_dao, _, user_id, _ = favorite_dao_context

    assert not favorite_dao.add_favorite(user_id, "unknown-station")


def test_list_favorites_from_database(favorite_station_dao):
    favorite_dao, station_dao, user_id, station_id = favorite_dao_context
    station = station_dao.get_by_id(station_id)
    assert station is not None
    assert favorite_dao.add_favorite(user_id, station_id)

    favorites = favorite_dao.list_favorites({"user_id": user_id})

    assert len(favorites) == 1
    assert favorites[0].station_id == station.station_id
    assert favorites[0].name == station.name


def test_list_favorites_for_unknown_user(favorite_station_dao):
    favorite_dao, _, user_id, _ = favorite_dao_context

    assert favorite_dao.list_favorites({"user_id": user_id + 10_000_000}) is None


def test_count_favorites_from_database(favorite_station_dao):
    favorite_dao, _, user_id, station_id = favorite_dao_context
    assert favorite_dao.add_favorite(user_id, station_id)

    assert favorite_dao.count_favorites([station_id]) == {station_id: 1}


def test_count_favorites_for_unknown_station(favorite_dafavorite_station_daoo_context):
    favorite_dao, _, _, _ = favorite_dao_context

    assert favorite_dao.count_favorites(["unknown-station"]) is None


def test_count_favorites_for_empty_input(favorite_station_dao):
    favorite_dao, _, _, _ = favorite_dao_context

    assert favorite_dao.count_favorites([]) == {}


def test_remove_favorite(favorite_station_dao):
    favorite_dao, _, user_id, station_id = favorite_dao_context
    assert favorite_dao.add_favorite(user_id, station_id)

    assert favorite_dao.remove_favorite(user_id, station_id)
    assert not favorite_dao.remove_favorite(user_id, station_id)

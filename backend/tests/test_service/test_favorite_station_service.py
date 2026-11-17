from unittest.mock import MagicMock

import pytest

from business_object.station_information import StationInformation
from dao.favorite_station_dao import FavoriteStationDAO
from service.favorite_station_service import FavoriteStationService


@pytest.fixture
def favorite_dao():
    return MagicMock(spec=FavoriteStationDAO)


def test_add_favorite_station_ok(favorite_dao):
    """L'ajout est transmis au DAO et son résultat est renvoyé."""

    # GIVEN
    user_id, station_id = 1, "station-1"
    favorite_dao.add_favorite.return_value = True
    service = FavoriteStationService(favorite_dao)

    # WHEN
    added = service.add_favorite_station(user_id, station_id)

    # THEN
    assert added
    favorite_dao.add_favorite.assert_called_once_with(user_id, station_id)


def test_add_favorite_station_failure(favorite_dao):
    """Le service renvoie l'échec communiqué par le DAO."""

    # GIVEN
    favorite_dao.add_favorite.return_value = False
    service = FavoriteStationService(favorite_dao)

    # WHEN
    added = service.add_favorite_station(1, "station-1")

    # THEN
    assert not added


def test_list_favorites_returns_dao_result(favorite_dao):
    """La liste et ses paramètres sont transmis tels quels au DAO avec valeurs par défaut."""

    # GIVEN
    user_id = 1
    favorite_dao.list_favorites.return_value = None
    service = FavoriteStationService(favorite_dao)

    # WHEN
    favorites = service.list_favorites(user_id)

    # THEN
    assert favorites is None
    favorite_dao.list_favorites.assert_called_once_with(user_id, 1, 10)


def test_list_favorites_with_pagination(favorite_dao):
    """La liste prend en compte les arguments page et size spécifiés."""

    # GIVEN
    user_id = 2
    mock_stations = [
        StationInformation(
            station_id="st_1",
            name="Station 1",
            short_name="S1",
            lat=48.8,
            lon=2.3,
            capacity=10,
        )
    ]
    favorite_dao.list_favorites.return_value = mock_stations
    service = FavoriteStationService(favorite_dao)

    # WHEN
    favorites = service.list_favorites(user_id, page=2, size=5)

    # THEN
    assert favorites == mock_stations
    favorite_dao.list_favorites.assert_called_once_with(2, 2, 5)


def test_remove_favorite_station_ok(favorite_dao):
    """Le retrait est transmis au DAO et son résultat est renvoyé."""

    # GIVEN
    user_id, station_id = 1, "station-1"
    favorite_dao.remove_favorite.return_value = True
    service = FavoriteStationService(favorite_dao)

    # WHEN
    removed = service.remove_favorite_station(user_id, station_id)

    # THEN
    assert removed
    favorite_dao.remove_favorite.assert_called_once_with(user_id, station_id)


def test_remove_favorite_station_failure(favorite_dao):
    """Le service renvoie l'échec communiqué par le DAO."""

    # GIVEN
    favorite_dao.remove_favorite.return_value = False
    service = FavoriteStationService(favorite_dao)

    # WHEN
    removed = service.remove_favorite_station(1, "station-1")

    # THEN
    assert not removed

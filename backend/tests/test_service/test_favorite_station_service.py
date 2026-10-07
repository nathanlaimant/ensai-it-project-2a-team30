from unittest.mock import MagicMock

from business_object.station_information import StationInformation
from dao.favorit_station_dao import FavoriteStationDao
from service.favorite_station_service import FavoriteStationService


# Tests de add_favorite_station() :

def test_add_favorite_station_ok():
    """L'ajout de la station à la liste des favoris de l'utilisateur est réussie"""

    # GIVEN
    id_user, id_station = 1, ""
    FavoriteStationDao().add_favorite(id_user, id_station) = MagicMock(return_value=True)

    # WHEN
    added = FavoriteStationService().add_favorite(id_user, id_station)

    # THEN
    assert added


def test_add_favorite_station_wrong_user():
    """L'identifiant de l'utilisateur n'est pas reconnu"""

    # GIVEN
    id_user, id_station = 1676769, ""
    FavoriteStationDao().add_favorite(id_user, id_station) = MagicMock(return_value=False)

    # WHEN
    added = FavoriteStationService().add_favorite(id_user, id_station)

    # THEN
    assert not added


def test_add_favorite_station_wrong_station():
    """L'identifiant de la station n'est pas reconnu"""

    # GIVEN
    id_user, id_station = 1, "fakeid"
    FavoriteStationDao().add_favorite(id_user, id_station) = MagicMock(return_value=False)

    # WHEN
    added = FavoriteStationService().add_favorite(id_user, id_station)

    # THEN
    assert not added


# Tests de list_favorites() :

def test_list_favorites_ok():
    """Nous réussissons à obtenir la liste des stations favorites d'un utilisateur donné"""


# Tests de remove_favorite_station() :

def test_remove_favorite_station_ok():
    """La station est bien retirée de la liste des stations favorites de l'utilisateur"""

    # GIVEN
    id_station, id_user = "", 1
    FavoriteStationDao().remove_favorite(id_user, id_station) = MagicMock(return_value=True)

    # WHEN
    removed = FavoriteStationService().remove_favorite_station(id_user, id_station)

    # THEN
    assert removed


def test_remove_favorite_station_wrong_user():
    """L'identifiant de l'utilisateur n'est pas reconnu pour retirer une station
    de la liste des favoris"""

    # GIVEN
    id_station, id_user = "", 5656576
    FavoriteStationDao().remove_favorite(id_user, id_station) = MagicMock(return_value=False)

    # WHEN
    removed = FavoriteStationService().remove_favorite_station(id_user, id_station)

    # THEN
    assert not removed


def test_remove_favorite_station_wrong_station():
    """La station n'est pas présente dans la liste des stations favorites de l'utilisateur"""

    # GIVEN
    id_station, id_user = "", 1
    FavoriteStationDao().remove_favorite(id_user, id_station) = MagicMock(return_value=False)

    # WHEN
    removed = FavoriteStationService().remove_favorite_station(id_user, id_station)

    # THEN
    assert not removed

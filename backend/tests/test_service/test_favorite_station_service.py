from unittest.mock import MagicMock

from business_object.station_information import StationInformation
from dao.favorit_station_dao import FavoriteStationDao
from service.favorite_station_service import FavoriteStationService


# Tests de add_favorite_station() :

def test_add_favorite_station_ok():
    """L'ajout de la station à la liste des favoris de l'utilisateur est réussie"""


def test_add_favorite_station_wrong_user():
    """L'ajout de la station à la liste des favoris de l'utilisateur échoue
    car l'identifiant de ce dernier n'est pas reconnu"""


def test_add_favorite_station_wrong_station():
    """L'ajout de la station à la liste des favoris de l'utilisateur échoue
    car l'identifiant de celle-ci n'est pas reconnu"""


# Tests de list_favorites() :




# Tests de remove_favorite_station() :

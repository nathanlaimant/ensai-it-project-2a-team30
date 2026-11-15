from pathlib import Path

import pytest

from business_object.station_information import StationInformation
from business_object.user import User
from dao.favorite_station_dao import FavoriteStationDAO
from dao.station_dao import StationDAO
from dao.user_dao import UserDAO
from utils.db_connection import DbConnection
from utils.settings import Settings

test_env_path = Path(__file__).resolve().parents[2] / ".test_env"


@pytest.fixture(scope="session")
def db_connection():
    """Fournit un pool de connexion à la base de données de test."""
    settings = Settings(_env_file=test_env_path if test_env_path.exists() else ".test_env")
    return DbConnection(settings)


@pytest.fixture
def favorite_station_dao(db_connection):
    return FavoriteStationDAO(db_connection)


@pytest.fixture(scope="session")
def initiate_stations_and_users(db_connection):
    """Insère les stations et utilisateurs nécessaires aux tests de favoris."""
    initial_stations = [
        StationInformation(
            station_id="fav_st_1",
            name="Station Favori 1",
            short_name="F1",
            lat=48.8566,
            lon=2.3522,
            address="1 Rue de Paris",
            is_virtual_station=False,
            station_area=None,
            contact_phone=None,
            capacity=10,
            is_charging_station=False,
        ),
        StationInformation(
            station_id="fav_st_2",
            name="Station Favori 2",
            short_name="F2",
            lat=48.8570,
            lon=2.3530,
            address="2 Rue de Paris",
            is_virtual_station=False,
            station_area=None,
            contact_phone=None,
            capacity=15,
            is_charging_station=True,
        ),
    ]

    initial_users = [
        User(
            username="fav_user_alice",
            password_hashed="hash_fav_1",
            email="fav_alice@test.fr",
            role="USER",
        ),
        User(
            username="fav_user_bob",
            password_hashed="hash_fav_2",
            email="fav_bob@test.fr",
            role="USER",
        ),
    ]

    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_favorite_station;")
                cur.execute("DELETE FROM station_information WHERE station_id IN ('fav_st_1', 'fav_st_2');")
                cur.execute("DELETE FROM \"user\" WHERE username IN ('fav_user_alice', 'fav_user_bob');")

    station_dao = StationDAO(db_connection)
    for st in initial_stations:
        station_dao.upsert_station_info(st)

    user_dao = UserDAO(db_connection)
    for u in initial_users:
        user_dao.create_user(u)

    yield {"stations": initial_stations, "users": initial_users}

    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_favorite_station;")
                cur.execute("DELETE FROM station_information WHERE station_id IN ('fav_st_1', 'fav_st_2');")
                cur.execute("DELETE FROM \"user\" WHERE username IN ('fav_user_alice', 'fav_user_bob');")


@pytest.fixture(autouse=True)
def setup_test_environment(db_connection, initiate_stations_and_users):
    """
    Nettoie la table user_favorite_station avant chaque test et s'assure
    que les données de référence existent.
    """
    station_dao = StationDAO(db_connection)
    for st in initiate_stations_and_users["stations"]:
        station_dao.upsert_station_info(st)

    user_dao = UserDAO(db_connection)
    for u in initiate_stations_and_users["users"]:
        existing_user = user_dao.get_by_username(u.username)
        if not existing_user:
            user_dao.create_user(u)
        else:
            u.user_id = existing_user.user_id

    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_favorite_station;")


# Tests de add_favorite()


def test_add_favorite_ok(favorite_station_dao, initiate_stations_and_users):
    """Ajout d'une station aux favoris d'un utilisateur réussi"""
    # GIVEN
    user = initiate_stations_and_users["users"][0]
    station = initiate_stations_and_users["stations"][0]

    # WHEN
    added = favorite_station_dao.add_favorite(user.user_id, station.station_id)

    # THEN
    assert added is True
    favorites = favorite_station_dao.list_favorites(user.user_id)
    assert favorites is not None
    assert len(favorites) == 1
    assert favorites[0].station_id == station.station_id


def test_add_favorite_duplicate(favorite_station_dao, initiate_stations_and_users):
    """Ajout d'une station déjà présente dans les favoris retourne False (pas de doublon)"""
    # GIVEN
    user = initiate_stations_and_users["users"][0]
    station = initiate_stations_and_users["stations"][0]
    favorite_station_dao.add_favorite(user.user_id, station.station_id)

    # WHEN
    second_add = favorite_station_dao.add_favorite(user.user_id, station.station_id)

    # THEN
    assert second_add is False


def test_add_favorite_for_unknown_user(favorite_station_dao, initiate_stations_and_users):
    """Ajout d'une station aux favoris échoue car l'utilisateur n'existe pas"""
    # GIVEN
    unknown_user_id = 999999
    station = initiate_stations_and_users["stations"][0]

    # WHEN
    added = favorite_station_dao.add_favorite(unknown_user_id, station.station_id)

    # THEN
    assert added is False


def test_add_favorite_for_unknown_station(favorite_station_dao, initiate_stations_and_users):
    """Ajout d'une station aux favoris échoue car la station n'existe pas"""
    # GIVEN
    user = initiate_stations_and_users["users"][0]
    unknown_station_id = "non_existent_station"

    # WHEN
    added = favorite_station_dao.add_favorite(user.user_id, unknown_station_id)

    # THEN
    assert added is False


# Tests de list_favorites()


def test_list_favorites_ok(favorite_station_dao, initiate_stations_and_users):
    """Récupération réussie de la liste des stations favorites d'un utilisateur"""
    # GIVEN
    user = initiate_stations_and_users["users"][0]
    station_1 = initiate_stations_and_users["stations"][0]
    station_2 = initiate_stations_and_users["stations"][1]
    favorite_station_dao.add_favorite(user.user_id, station_1.station_id)
    favorite_station_dao.add_favorite(user.user_id, station_2.station_id)

    # WHEN
    favorites = favorite_station_dao.list_favorites(user.user_id)

    # THEN
    assert favorites is not None
    assert len(favorites) == 2
    fav_ids = {f.station_id for f in favorites}
    assert fav_ids == {station_1.station_id, station_2.station_id}


def test_list_favorites_empty(favorite_station_dao, initiate_stations_and_users):
    """Retourne une liste vide lorsque l'utilisateur n'a aucun favori"""
    # GIVEN
    user = initiate_stations_and_users["users"][1]

    # WHEN
    favorites = favorite_station_dao.list_favorites(user.user_id)

    # THEN
    assert favorites == []


def test_list_favorites_unknown_user(favorite_station_dao):
    """Retourne None lorsque l'utilisateur n'existe pas"""
    # GIVEN
    unknown_user_id = 999999

    # WHEN
    favorites = favorite_station_dao.list_favorites(unknown_user_id)

    # THEN
    assert favorites is None


def test_list_favorites_pagination(favorite_station_dao, initiate_stations_and_users):
    """Pagination réussie pour list_favorites"""
    # GIVEN
    user = initiate_stations_and_users["users"][0]
    station_1 = initiate_stations_and_users["stations"][0]
    station_2 = initiate_stations_and_users["stations"][1]
    favorite_station_dao.add_favorite(user.user_id, station_1.station_id)
    favorite_station_dao.add_favorite(user.user_id, station_2.station_id)

    # WHEN
    page_1 = favorite_station_dao.list_favorites(user.user_id, page=1, size=1)
    page_2 = favorite_station_dao.list_favorites(user.user_id, page=2, size=1)

    # THEN
    assert len(page_1) == 1
    assert len(page_2) == 1
    assert page_1[0].station_id != page_2[0].station_id


# Tests de count_favorites()


def test_count_favorites_ok(favorite_station_dao, initiate_stations_and_users):
    """Comptage réussi du nombre d'utilisateurs ayant mis des stations en favori"""
    # GIVEN
    user_1 = initiate_stations_and_users["users"][0]
    user_2 = initiate_stations_and_users["users"][1]
    station_1 = initiate_stations_and_users["stations"][0]
    station_2 = initiate_stations_and_users["stations"][1]

    favorite_station_dao.add_favorite(user_1.user_id, station_1.station_id)
    favorite_station_dao.add_favorite(user_1.user_id, station_2.station_id)
    favorite_station_dao.add_favorite(user_2.user_id, station_1.station_id)

    # WHEN
    counts = favorite_station_dao.count_favorites([station_1.station_id, station_2.station_id])

    # THEN
    assert counts == {station_1.station_id: 2, station_2.station_id: 1}


def test_count_favorites_zero_favorites(favorite_station_dao, initiate_stations_and_users):
    """Comptage retourne 0 pour une station existante sans aucun favori"""
    # GIVEN
    station_2 = initiate_stations_and_users["stations"][1]

    # WHEN
    counts = favorite_station_dao.count_favorites([station_2.station_id])

    # THEN
    assert counts == {station_2.station_id: 0}


def test_count_favorites_empty_list(favorite_station_dao):
    """Retourne {} lorsque la liste d'identifiants est vide"""
    # WHEN
    counts = favorite_station_dao.count_favorites([])

    # THEN
    assert counts == {}


def test_count_favorites_unknown_station(favorite_station_dao, initiate_stations_and_users):
    """Retourne None lorsqu'au moins un des identifiants de station n'existe pas"""
    # GIVEN
    station_1 = initiate_stations_and_users["stations"][0]

    # WHEN
    counts = favorite_station_dao.count_favorites([station_1.station_id, "unknown_station_id"])

    # THEN
    assert counts is None


# Tests de remove_favorite()


def test_remove_favorite_ok(favorite_station_dao, initiate_stations_and_users):
    """Suppression d'une station des favoris d'un utilisateur réussie"""
    # GIVEN
    user = initiate_stations_and_users["users"][0]
    station = initiate_stations_and_users["stations"][0]
    favorite_station_dao.add_favorite(user.user_id, station.station_id)

    # WHEN
    removed = favorite_station_dao.remove_favorite(user.user_id, station.station_id)

    # THEN
    assert removed is True
    favorites = favorite_station_dao.list_favorites(user.user_id)
    assert favorites == []


def test_remove_favorite_not_favorited(favorite_station_dao, initiate_stations_and_users):
    """Suppression échoue lorsque la station n'était pas dans les favoris"""
    # GIVEN
    user = initiate_stations_and_users["users"][0]
    station = initiate_stations_and_users["stations"][1]

    # WHEN
    removed = favorite_station_dao.remove_favorite(user.user_id, station.station_id)

    # THEN
    assert removed is False


def test_remove_favorite_unknown_user(favorite_station_dao, initiate_stations_and_users):
    """Suppression échoue lorsque l'utilisateur n'existe pas"""
    # GIVEN
    unknown_user_id = 999999
    station = initiate_stations_and_users["stations"][0]

    # WHEN
    removed = favorite_station_dao.remove_favorite(unknown_user_id, station.station_id)

    # THEN
    assert removed is False

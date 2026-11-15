from pathlib import Path

import pytest

from business_object.station_information import StationInformation
from dao.station_dao import StationDAO
from utils.db_connection import DbConnection
from utils.settings import Settings

test_env_path = Path(__file__).resolve().parents[2] / ".test_env"


@pytest.fixture(scope="session")
def db_connection():
    """Fournit un pool de connexion à la base de données de test."""
    settings = Settings(_env_file=test_env_path if test_env_path.exists() else ".test_env")
    return DbConnection(settings)


@pytest.fixture
def station_dao(db_connection):
    return StationDAO(db_connection)


@pytest.fixture
def sample_stations():
    """Génère une liste isolée d'objets StationInformation pour chaque test."""
    return [
        StationInformation(
            station_id="101",
            name="Station Alpha",
            short_name="A101",
            lat=48.8566,
            lon=2.3522,
            address="1 Rue de Paris",
            is_virtual_station=False,
            station_area=None,
            contact_phone="0102030405",
            capacity=20,
            is_charging_station=True,
        ),
        StationInformation(
            station_id="102",
            name="Station Beta",
            short_name="B102",
            lat=48.8570,
            lon=2.3530,
            address="2 Rue de Paris",
            is_virtual_station=False,
            station_area=None,
            contact_phone=None,
            capacity=10,
            is_charging_station=False,
        ),
        StationInformation(
            station_id="103",
            name="Station Gamma",
            short_name="G103",
            lat=48.5734,
            lon=7.7521,
            address="3 Rue de Strasbourg",
            is_virtual_station=True,
            station_area=None,
            contact_phone=None,
            capacity=30,
            is_charging_station=False,
        ),
    ]


@pytest.fixture(autouse=True)
def setup_test_environment(db_connection):
    """Nettoie la table station_information avant chaque test."""
    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_favorite_station;")
                cur.execute("DELETE FROM station_status_hourly;")
                cur.execute("DELETE FROM station_status;")
                cur.execute("DELETE FROM station_information;")
    yield
    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_favorite_station;")
                cur.execute("DELETE FROM station_status_hourly;")
                cur.execute("DELETE FROM station_status;")
                cur.execute("DELETE FROM station_information;")


@pytest.fixture
def inserted_stations(station_dao, sample_stations):
    """Insère les stations d'exemple en base de données et les retourne."""
    for st in sample_stations:
        station_dao.upsert_station_info(st)
    return sample_stations


# Tests de upsert_station_info()


def test_upsert_station_info_ok(station_dao, sample_stations):
    """Insertion d'une nouvelle station réussie"""
    # GIVEN
    station = sample_stations[0]

    # WHEN
    added = station_dao.upsert_station_info(station)

    # THEN
    assert added is True
    retrieved = station_dao.get_by_id(station.station_id)
    assert retrieved is not None
    assert retrieved.station_id == station.station_id
    assert retrieved.name == station.name
    assert retrieved.capacity == station.capacity


def test_upsert_station_info_update_conflict(station_dao, sample_stations):
    """Mise à jour d'une station existante lors d'un conflit sur station_id réussie"""
    # GIVEN
    station = sample_stations[0]
    station_dao.upsert_station_info(station)

    updated_station = StationInformation(
        station_id=station.station_id,
        name="Station Alpha Modifiée",
        short_name="A101_MOD",
        lat=48.8566,
        lon=2.3522,
        address="10 Rue Modifiée",
        is_virtual_station=False,
        station_area=None,
        contact_phone="0999999999",
        capacity=25,
        is_charging_station=False,
    )

    # WHEN
    updated = station_dao.upsert_station_info(updated_station)

    # THEN
    assert updated is True
    retrieved = station_dao.get_by_id(station.station_id)
    assert retrieved is not None
    assert retrieved.name == "Station Alpha Modifiée"
    assert retrieved.short_name == "A101_MOD"
    assert retrieved.capacity == 25
    assert retrieved.is_charging_station is False


def test_upsert_station_info_fail_none(station_dao):
    """L'insertion échoue et retourne False lorsque l'objet station est None"""
    # WHEN
    added = station_dao.upsert_station_info(None)

    # THEN
    assert added is False


# Tests de get_by_id()


def test_get_by_id_ok(station_dao, inserted_stations):
    """Recherche d'une station par son identifiant réussie"""
    # GIVEN
    target_id = inserted_stations[0].station_id

    # WHEN
    station = station_dao.get_by_id(target_id)

    # THEN
    assert station is not None
    assert isinstance(station, StationInformation)
    assert station.station_id == target_id
    assert station.name == inserted_stations[0].name
    assert station.lat == pytest.approx(inserted_stations[0].lat)
    assert station.lon == pytest.approx(inserted_stations[0].lon)


def test_get_by_id_fail_unknown(station_dao, inserted_stations):
    """Recherche d'une station retourne None car l'identifiant n'existe pas"""
    # GIVEN
    unknown_id = "fake_station_id"

    # WHEN
    station = station_dao.get_by_id(unknown_id)

    # THEN
    assert station is None


# Tests de get_nearby()


def test_get_nearby_ok(station_dao, inserted_stations):
    """Recherche de stations proches réussie dans un rayon donné"""
    # GIVEN
    # Station 101 est à (48.8566, 2.3522), Station 102 est à ~74m, Station 103 est à Strasbourg
    lat, lon = 48.8566, 2.3522
    radius_meters = 150.0

    # WHEN
    nearby_stations = station_dao.get_nearby(lat, lon, radius_meters)

    # THEN
    assert nearby_stations is not None
    assert isinstance(nearby_stations, list)
    station_ids = [s.station_id for s in nearby_stations]
    assert "101" in station_ids
    assert "102" in station_ids
    assert "103" not in station_ids


def test_get_nearby_none_found(station_dao, inserted_stations):
    """Recherche de stations proches retourne None lorsqu'aucune station n'est dans le rayon"""
    # GIVEN
    lat, lon = 0.0, 0.0
    radius_meters = 100.0

    # WHEN
    nearby_stations = station_dao.get_nearby(lat, lon, radius_meters)

    # THEN
    assert nearby_stations is None


# Tests de list_stations()


def test_list_stations_no_params(station_dao, inserted_stations):
    """Retourne l'ensemble des stations sans filtre"""
    # WHEN
    stations = station_dao.list_stations()

    # THEN
    assert stations is not None
    assert isinstance(stations, list)
    assert len(stations) == len(inserted_stations)
    for s in stations:
        assert isinstance(s, StationInformation)


def test_list_stations_filter_name(station_dao, inserted_stations):
    """Filtrage réussi par nom partiel de station"""
    # WHEN
    stations = station_dao.list_stations(name="Alpha")

    # THEN
    assert len(stations) == 1
    assert stations[0].station_id == "101"
    assert stations[0].name == "Station Alpha"


def test_list_stations_filter_short_name(station_dao, inserted_stations):
    """Filtrage réussi par nom court de station"""
    # WHEN
    stations = station_dao.list_stations(short_name="B102")

    # THEN
    assert len(stations) == 1
    assert stations[0].station_id == "102"


def test_list_stations_filter_capacity(station_dao, inserted_stations):
    """Filtrage réussi par capacité minimale et maximale"""
    # WHEN
    min_cap_stations = station_dao.list_stations(min_capacity=15)
    max_cap_stations = station_dao.list_stations(max_capacity=15)

    # THEN
    # 101 a une capacité de 20, 103 a une capacité de 30
    assert len(min_cap_stations) == 2
    min_ids = {s.station_id for s in min_cap_stations}
    assert min_ids == {"101", "103"}

    # 102 a une capacité de 10
    assert len(max_cap_stations) == 1
    assert max_cap_stations[0].station_id == "102"


def test_list_stations_filter_is_virtual_station(station_dao, inserted_stations):
    """Filtrage réussi par station virtuelle"""
    # WHEN
    virtual_stations = station_dao.list_stations(is_virtual_station=True)

    # THEN
    assert len(virtual_stations) == 1
    assert virtual_stations[0].station_id == "103"


def test_list_stations_filter_charging_station(station_dao, inserted_stations):
    """Filtrage réussi par borne de recharge"""
    # WHEN
    charging_stations = station_dao.list_stations(is_charging_station=True)

    # THEN
    assert len(charging_stations) == 1
    assert charging_stations[0].station_id == "101"


def test_list_stations_pagination(station_dao, inserted_stations):
    """Pagination réussie pour list_stations"""
    # WHEN
    page_1 = station_dao.list_stations(page=1, size=2)
    page_2 = station_dao.list_stations(page=2, size=2)

    # THEN
    assert len(page_1) == 2
    assert len(page_2) == 1
    assert page_1[0].station_id != page_2[0].station_id


def test_list_stations_no_match(station_dao, inserted_stations):
    """Retourne une liste vide lorsqu'aucun critère ne correspond"""
    # WHEN
    stations = station_dao.list_stations(name="NomInexistantAbsolument")

    # THEN
    assert stations == []

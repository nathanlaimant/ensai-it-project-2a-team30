from pathlib import Path
from unittest.mock import MagicMock

import pytest

from business_object.station_information import StationInformation
from dao.station_dao import StationDAO
from utils.db_connection import DbConnection
from utils.settings import Settings

test_env_path = Path(__file__).resolve().parents[2] / ".test_env"


@pytest.fixture(scope="session")
def db_connection():
    """Fournit un pool de connexion à la base de données de test."""
    settings = Settings(
        _env_file=test_env_path if test_env_path.exists() else ".test_env"
    )
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


def test_upsert_station_info_with_station_area(station_dao):
    """Insertion réussie d'une station avec station_area au format JSON"""
    # GIVEN
    area_payload = {
        "type": "Polygon",
        "coordinates": [[[7.7, 48.6], [7.8, 48.6], [7.8, 48.7], [7.7, 48.6]]],
    }
    station = StationInformation(
        station_id="104_area",
        name="Station Zone",
        short_name="Z104",
        lat=48.65,
        lon=7.75,
        address="Rue de la Zone",
        is_virtual_station=True,
        station_area=area_payload,
        contact_phone=None,
        capacity=5,
        is_charging_station=None,
    )

    # WHEN
    added = station_dao.upsert_station_info(station)

    # THEN
    assert added is True
    retrieved = station_dao.get_by_id(station.station_id)
    assert retrieved is not None
    assert retrieved.station_area == area_payload


def test_upsert_station_info_db_exception():
    """upsert_station_info retourne False lors d'une exception de base de données"""
    mock_db = MagicMock()
    mock_db.get_connection.side_effect = Exception("Erreur de connexion DB")
    dao = StationDAO(mock_db)

    station = StationInformation(
        station_id="fail_id",
        name="Station Fail",
        short_name="F",
        lat=0.0,
        lon=0.0,
        capacity=1,
    )
    assert dao.upsert_station_info(station) is False


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


def test_list_stations_filter_by_extra_attributes(station_dao, inserted_stations):
    """Filtrage réussi par station_id, address, contact_phone, lat, lon et capacity exacte"""
    # station 101: address="1 Rue de Paris", contact_phone="0102030405", lat=48.8566, lon=2.3522, capacity=20
    by_id = station_dao.list_stations(station_id="101")
    assert len(by_id) == 1 and by_id[0].station_id == "101"

    by_addr = station_dao.list_stations(address="Paris")
    assert len(by_addr) == 2

    by_phone = station_dao.list_stations(contact_phone="010203")
    assert len(by_phone) == 1 and by_phone[0].station_id == "101"

    by_coords = station_dao.list_stations(lat=48.8566, lon=2.3522)
    assert len(by_coords) == 1 and by_coords[0].station_id == "101"

    by_exact_cap = station_dao.list_stations(capacity=20)
    assert len(by_exact_cap) == 1 and by_exact_cap[0].station_id == "101"


def test_station_dao_methods_raise_on_db_exception():
    """Les méthodes de lecture de StationDAO lèvent l'exception en cas d'erreur DB"""
    mock_db = MagicMock()
    mock_db.get_connection.side_effect = Exception("Erreur DB lecture")
    dao = StationDAO(mock_db)

    with pytest.raises(Exception, match="Erreur DB lecture"):
        dao.get_by_id("101")

    with pytest.raises(Exception, match="Erreur DB lecture"):
        dao.get_nearby(48.85, 2.35, 100.0)

    with pytest.raises(Exception, match="Erreur DB lecture"):
        dao.list_stations()


def test_upsert_station_info_fetchone_none():
    """Vérifie le retour False si le fetchone ne retourne aucun enregistrement"""
    mock_db = MagicMock()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_db.get_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    dao = StationDAO(mock_db)
    st = StationInformation(
        station_id="st_none",
        name="Test",
        lat=48.0,
        lon=2.0,
        capacity=10,
    )
    assert dao.upsert_station_info(st) is False

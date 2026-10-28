from datetime import datetime, timedelta
from unittest.mock import MagicMock

from business_object.station_information import StationInformation
from business_object.station_status import StationStatus
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from service.station_service import StationService

debut = datetime(year=1970, month=1, hour=0, minute=0, second=0)

stations = [
  StationInformation(
        station_id="213688169",
        name="Benjamin Godard - Victor Hugo",
        short_name="16107",
        lat=48.865983,
        lon=2.275725,
        capacity=35
    ),
  StationInformation(
        station_id="19179944124",
        name="Hôpital Mondor",
        short_name="40001",
        lat=48.798922410229,
        lon=2.4537451531298,
        capacity=28
    ),
  StationInformation(
        station_id="18795078746",
        name="Charcot - Benfleet",
        short_name="32304",
        lat=48.878370277021,
        lon=2.440523876268,
        capacity=28
    ),
  StationInformation(
        station_id="36255",
        name="Toudouze - Clauzel",
        short_name="9020",
        lat=48.87929591733507,
        lon=2.3373600840568547,
        capacity=21
    )
]

statuses = [
  StationStatus(
    station_id="213688169",
    num_bikes_available=23,
    num_docks_available=11,
    operational_capacity=34,
    last_reported=debut + timedelta(seconds=1792526423),
    vehicule_types_available=[{"mechanical": 16}, {"ebike": 7}],
    station_state="FUNCTIONAL"
  ),
  StationStatus(
    station_id="19179944124",
    num_bikes_available=21,
    num_docks_available=7,
    operational_capacity=28,
    last_reported=debut + timedelta(seconds=1792526596),
    vehicule_types_available=[{"mechanical": 12}, {"ebike": 9}],
    station_state="FUNCTIONAL"
  ),
  StationStatus(
    station_id="18795078746",
    num_bikes_available=4,
    num_docks_available=25,
    operational_capacity=29,
    last_reported=debut + timedelta(seconds=1792526599),
    vehicule_types_available=[{"mechanical": 1}, {"ebike": 3}],
    station_state="FUNCTIONAL"
  ),
  StationStatus(
    station_id="36255",
    num_bikes_available=6,
    num_docks_available=15,
    operational_capacity=21,
    last_reported=debut + timedelta(seconds=1792526434),
    vehicule_types_available=[{"mechanical": 4}, {"ebike": 2}],
    station_state="FUNCTIONAL"
  )
]


# Tests de get_by_id()

def test_get_by_id_ok():
    """Nous réussissons à obtenir la bonne station"""

    # GIVEN
    station_id = stations[3].station_id
    StationDAO().get_by_id = MagicMock(return_value=stations[3])

    # WHEN
    station = StationService().get_by_id(station_id)

    # THEN
    assert station is not None
    assert station_id == station.station_id


def test_get_by_id_fail():
    """Échec de l'obtention des information de la station car l'identifiant
    n'est pas reconnu"""

    # GIVEN
    id = "fakeid"
    StationDAO().get_by_id(return_value=None)

    # WHEN
    station = StationService().get_by_id(id)

    # THEN
    assert station is None


# Tests de list_stations()


def test_list_stations_no_params():
    """Nous réussissons à obtenir la liste des stations"""

    # GIVEN
    StationDAO().list_stations = MagicMock(return_value=stations)

    # WHEN
    res = StationService().list_stations()

    # THEN
    assert len(res) == 4
    for s in res:
        assert isinstance(s, StationInformation)


def test_list_stations_with_params():
    """Nous réussissons à obtenir la liste des stations"""

    # GIVEN
    StationDAO().list_stations = MagicMock(return_value=stations[3])

    # WHEN
    res = StationService().list_stations(name="Toudouze - Clauzel")

    # THEN
    assert len(res) == 1
    assert isinstance(res[0], StationInformation)


# Tests de get_station_current_status()

def test_get_station_current_status_ok():
    """Nous réussissons à obtenir la mise à jour la plus récente du statut de la station"""

    # GIVEN
    station_id = "213688169"
    StationStatusDAO().get_latest_status = MagicMock(return_value=statuses[0])

    # WHEN
    res = StationService().get_current_status(station_id)

    # THEN
    assert res is not None
    assert isinstance(res, StationStatus)


def test_get_station_current_status_non_existing():
    """Nous échouons à obtenir la mise à jour la plus récente du statut de la station
    car l'identifiant n'est pas reconnu"""

    # GIVEN
    station_id = "fake_id"
    StationStatusDAO().get_latest_status = MagicMock(return_value=None)

    # WHEN
    res = StationService().get_current_status(station_id)

    # THEN
    assert res is None


# Tests de get_station_history()

def test_get_station_history_no_params():
    """Nous réussions à obtenir l'historique de la station demandée sans critères demandés"""

    # GIVEN
    station_id = "213688169"
    StationStatusDAO().get_one_station_history = MagicMock(return_value=statuses[0])

    # WHEN
    history = StationService().get_station_history(station_id)

    # THEN
    assert isinstance(history[0], StationStatus)
    assert len(history) == 1


def test_get_station_history_with_params():
    """Nous réussissons à obtenir l'historique de la station demandée avec un critère sur
    la période"""

    # GIVEN
    station_id = "18795078746"
    start_time = debut + timedelta(seconds=1792526580)
    end_time = debut + timedelta(seconds=1792526598)
    StationStatusDAO().get_one_station_history = MagicMock(return_value=[])

    # WHEN
    history = StationService().get_station_history(station_id, start_time, end_time)

    # THEN
    assert len(history) == 0

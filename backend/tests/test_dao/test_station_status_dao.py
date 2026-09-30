import os
from unittest.mock import patch
from datetime import datetime, timedelta

import psycopg3
import pytest
from utils.reset_database import ResetDatabase

from business_object.station_status import StationStatus
from dao.station_status_dao import StationStatusDao

first_date_counted = datetime.datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)

# Pour ne passer par la fonction StationDao().get_by_id()
stations = [
    StationInformation(
        station_id="16bbf68d-685a-4799-9bba-8915f10700e0",
        is_virtual_station=True,
        lat=48.8727256662692,
        lon=2.35437813765038,
        name="id_38206",
        capacity=3
    ),
    StationInformation(
        station_id="b42cb6d7-0558-4589-ad71-63e374fdb784",
        name="id_34235",
        is_virtual_station=True,
        lat=48.8266089252496,
        lon=2.33467058582095,
        capacity=3
    ),
    StationInformation(
        station_id="5770705c-cbb1-4baa-a1ca-eb40540b2f40",
        name="17 RUE DU VIEUX COLOMBIER",
        is_virtual_station=True,
        lat=48.851759,
        lon=2.3306,
        capacity=3
    ),
    StationInformation(
        station_id="74a3f9a1-70b0-4d9a-a1d1-bbb5c6948840",
        name="id_old844604G20081106092237,
        is_virtual_station=True,
        lat=48.8322843827352,
        lon=2.32105516137791,
        capacity=3
    )
]

# Trouver des station_status_id
status = [
    StationStatus(
        station_status_id=1,
        station_id="16bbf68d-685a-4799-9bba-8915f10700e0",
        num_bikes_available=0,
        operational_capacity=stations[0].capacity,
        is_installed=True,
        is_renting=True,
        is_returning=True,
        last_reported=first_date_counted + timedelta(seconds=1790760336),
        station_state="EMPTY"
    ),
    StationStatus(
        station_status_id=2,
        station_id="b42cb6d7-0558-4589-ad71-63e374fdb784",
        num_bikes_available=0,
        operational_capacity=stations[1].capacity,
        is_installed=True,
        is_renting=True,
        is_returning=True,
        last_reported=first_date_counted + timedelta(seconds=1790676268),
        station_state="EMPTY"
    ),
    StationStatus(
        station_status_id=3,
        station_id="5770705c-cbb1-4baa-a1ca-eb40540b2f40",
        num_bikes_available=0,
        operational_capacity=stations[2].capacity,
        is_installed=True,
        is_renting=True,
        is_returning=True,
        last_reported=first_date_counted + timedelta(seconds=1790247765),
        station_state="EMPTY"
    ),
    StationStatus(
        station_status_id=4,
        station_id="74a3f9a1-70b0-4d9a-a1d1-bbb5c6948840",
        num_bikes_available=0,
        operational_capacity=stations[3].capacity,
        is_installed=True,
        is_renting=True,
        is_returning=True,
        last_reported=first_date_counted + timedelta(seconds=1790751940),
        station_state="EMPTY"
    )
]


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation de la base de données pour les tests"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


# Tests de bulk_insert_status()

def test_bulk_insert_status_ok():
    """Insertions du nouveau statut des stations réussies"""

    # GIVEN
    number_status = len(status)

    # WHEN
    updates_made = StationStatusDao().bulk_insert_status(status)

    # THEN
    assert len(updates_made) == number_status


def test_bulk_insert_status_fail():
    """Insertion du nouveau statut des stations incomplète car toutes les stations
    à mettre à jour n'ont pas été intégrées en argument de la fonction"""

    # GIVEN
    number_status = len(status)

    # WHEN
    updates_made = StationStatusDao().bulk_insert_status(status[-1])

    # THEN
    assert len(updates_made) != number_status


# Tests de get_latest_status()

def test_get_latest_status_ok():
    """Mise à jour de la station réussie"""

    # GIVEN
    id_station = status[1].station_id

    # WHEN
    status = StationStatusDao().get_latest_status(id_station)

    # THEN
    assert status is not None
    assert status.station_id == id_station


def test_get_latest_status_fail():
    """Mise à jour de la station impossible car l'identifiant n'existe pas"""

    # GIVEN
    id_station = "fakeid"

    # WHEN
    status = StationStatusDao().get_latest_status(id_station)

    # THEN
    assert status is None


# Tests de get_status_history()

def test_get_status_history_ok():
    """Nous réussissons à obtenir l'historique du statut d'une station sur une période donnée"""

    # GIVEN
    station_id = status[2].station_id
    start_time, end_time = 1, 1

    # WHEN
    status_history = StationStatusDao().get_status_history(station_id, start_time, end_time)

    # THEN
    for s in status_history:
        assert s.station_id == station_id
        assert (end_time >= s.last_reported and start_time <= s.last_reported)

def test_get_status_history_fail():
    """Nous échouons à obtenir l'historique du statut d'une station car son identifiant n'est
    pas reconnu"""

    # GIVEN
    station_id = "fakeid"
    start_time, end_time = 1, 1

    # WHEN
    status_history = StationStatusDao().get_status_history(station_id, start_time, end_time)

    # THEN
    assert status_history is None

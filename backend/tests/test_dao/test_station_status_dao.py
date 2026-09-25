import os
from unittest.mock import patch
from datetime import datetime

import psycopg2
import pytest
from utils.reset_database import ResetDatabase

from business_object.station_status import StationStatus
from dao.station_status_dao import StationStatusDao

status = [
    StationStatus(),
    StationStatus(),
    StationStatus(),
    StationStatus()
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
        assert end_time >= s.last_reported
        assert start_time <= s.last_reported
import os
from unittest.mock import patch
from datetime import datetime

import psycopg3
import pytest
from utils.reset_database import ResetDatabase

from business_object.station_status_hourly import StationStatusHourly
from dao.station_status_hourly_dao import StationStatusHourlyDAO

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation de la base de données pour les tests"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


# Tests de bulk_insert_hourly_stats() :

def test_bulk_insert_hourly_stats_ok():
    """Insertions des statuts par heure des stations réussie"""


def test_bulk_insert_hourly_stats_fail():
    """Insertion ds statuts par heure des stations incomplète car toutes les stations
    à mettre à jour n'ont pas été intégrées en argument de la fonction"""


# Tests de get_hourly_stats() :

def test_get_hourly_stats_ok():
    """Nous réussions à voir les statuts par heure de la station donnée
    sur la période définie"""


def test_get_hourly_stats_wrong_id():
    """Nous ne pouvons pas obtenir les statuts par heure de la station donnée
    car son identifiant n'est pas reconnu"""


def test_get_hourly_stats_wrond_time():
    """Nous ne pouvons pas obtenir les statuts par heure de la station donnée
    car la période n'est pas disponible dans la base de données"""


# Tests de aggregate_daily_stats() :

def test_aggregate_daily_stats_ok():
    """Aggrégation des stats journalières de la station réussie"""


def test_aggregate_daily_stats_wrong_id():
    """Agrégation des données impossible car la station n'est pas reconnue"""


def test_aggregate_daily_stats_wrong_time():
    """Agrégagtion des données impossibles car la période donnée est indisponible
    dans la base de données"""

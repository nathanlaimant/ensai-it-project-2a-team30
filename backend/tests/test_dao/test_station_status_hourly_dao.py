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




# Tests de get_hourly_stats() :




# Tests de aggregate_daily_stats() :

def test_aggregate_daily_stats_ok():
    """Aggrégation des stats journalières des stations réussie"""

import os
from unittest.mock import patch
from datetime import datetime

import psycopg3
import pytest
from utils.reset_database import ResetDatabase

from business_object.station_status_hourly import StationStatusHourly
from dao.station_status_hourly_dao import StationStatusHourlyDAO

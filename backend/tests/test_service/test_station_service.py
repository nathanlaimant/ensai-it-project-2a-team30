from unittest.mock import MagicMock

from business_object.station_information import StationInformation
from dao.station_dao import StationDao
from service.station_service import StationService

stations = [
  StationInformation(),
  StationInformation(),
  StationInformation()
]


# Tests de list_stations()

def test_list_stations_no_params():
  """Nous réussissons à obtenir la liste des stations"""

  # GIVEN
  StationDao().list_stations = MagicMock(return_value=stations)

  # WHEN
  res = StationService().list_stations()

  # THEN
  assert len(res) == 3


def test_list_stations_with_params():
  """Nous réussissons à obtenir la liste des stations"""

  # GIVEN
  StationDao().list_stations = MagicMock(return_value=stations)

  # WHEN
  res = StationService().list_stations({"name": "id_3"})

  # THEN
  assert len(res) == 2


# Tests de get_station_current_status()

def test_get_station_current_status():
  """Nous réussissons à obtenir la mise à jour la plus récente du statut de la station"""

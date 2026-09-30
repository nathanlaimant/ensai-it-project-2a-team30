from unittest.mock import MagicMock

from business_object.station_information import StationInformation
from dao.station_dao import StationDao
from service.station_service import StationService

stations = [
  StationInformation(),
  StationInformation(),
  StationInformation()
]

statuses = [
  StationStatus(),
  StationStatus(),
  StationStatus(),
  StationStatus()
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

def test_get_station_current_status_ok():
  """Nous réussissons à obtenir la mise à jour la plus récente du statut de la station"""

  # GIVEN
  station_id = stations[0].station_id
  StationStatusDao().get_latest_status(station_id) = MagicMock(
    return_value=StationStatus()
  )

  # WHEN
  res = StationService().get_current_status(station_id)

  # THEN
  assert res is not None


def test_get_station_current_status_non_existing():
  """Nous échouons à obtenir la mise à jour la plus récente du statut de la station
  car l'identifiant n'est pas reconnu"""

  # GIVEN
  station_id = "fake_id"

  # WHEN
  res = StationService().get_current_status(station_id)

  # THEN
  assert res is None


# Tests de get_station_history()

def test_get_status_history_no_params():
  """Nous réussions à obtenir l'historique de la station demandée sans critères demandés"""

  # GIVEN
  station_id = stations[2].station_id
  StationStatusDao().get_status_history(station_id, start_time, end_time) = MagicMock(
    return_value=statuses
  )

  # WHEN
  history = StationService().get_status_history({"station_id": station_id})

  # THEN
  for s in history:
    assert isinstance(s, dict)
  assert len(history) == 4 # Dans la bdd de tests, on va mettre 4 statuts différents pour chaque station


def test_get_status_history_with_params():
  """Nous réussissons à obtenir l'historique de la station demandée avec un critère sur
  la période"""

  # GIVEN
  station_id, start_time, end_time = stations[2].station_id, 1, 1
  StationStatusDao().get_status_history(station_id, start_time, end_time) = MagicMock(
    return_value=statuses[-1]
  )

  # WHEN
  history = StationService().get_status_history(
    {
      "station_id": station_id,
      "start_time": start_time,
      "end_time": end_time
    }
  )

  # THEN
  for s in history:
    assert isinstance(s, dict)
  assert len(history) == 3 # Il faudrait exclure le statut le plus ancien dans le test

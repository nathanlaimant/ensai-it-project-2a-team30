from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from business_object.station_information import StationInformation
from dao.station_dao import StationDAO
from service.schedule.data_ingestion.station_information_strategy import (
    StationInformationStrategy,
)


@pytest.fixture
def mock_dao():
    return MagicMock(spec=StationDAO)


@pytest.fixture
def mock_http_client():
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def strategy(mock_dao, mock_http_client):
    return StationInformationStrategy(
        dao=mock_dao,
        feed_name="station_information",
        url="https://api.test/station_information.json",
        http_client=mock_http_client,
    )


# --- Tests de from_json_dict() ---


def test_from_json_dict_full(strategy):
    """Vérifie la conversion complète d'un dictionnaire JSON en StationInformation."""
    payload = {
        "station_id": "st_001",
        "name": "Station République",
        "short_name": "REP",
        "lat": 48.8675,
        "lon": 2.3638,
        "address": "Place de la République",
        "is_virtual_station": False,
        "station_area": {"type": "Polygon", "coordinates": []},
        "contact_phone": "0102030405",
        "capacity": 35,
        "is_charging_station": True,
    }

    st = strategy.from_json_dict(payload)

    assert isinstance(st, StationInformation)
    assert st.station_id == "st_001"
    assert st.name == "Station République"
    assert st.short_name == "REP"
    assert st.lat == 48.8675
    assert st.lon == 2.3638
    assert st.address == "Place de la République"
    assert st.is_virtual_station is False
    assert st.station_area == {"type": "Polygon", "coordinates": []}
    assert st.contact_phone == "0102030405"
    assert st.capacity == 35
    assert st.is_charging_station is True


def test_from_json_dict_minimal_and_none_fields(strategy):
    """Vérifie la conversion lorsque les champs optionnels sont None ou absents."""
    payload = {
        "station_id": "st_002",
        "name": "Station Minimale",
        "lat": "48.85",
        "lon": "2.35",
        "is_virtual_station": None,
        "capacity": None,
        "is_charging_station": None,
    }

    st = strategy.from_json_dict(payload)

    assert st.station_id == "st_002"
    assert st.name == "Station Minimale"
    assert st.lat == 48.85
    assert st.lon == 2.35
    assert st.short_name is None
    assert st.address is None
    assert st.is_virtual_station is None
    assert st.capacity is None
    assert st.is_charging_station is None


# --- Tests de parse_payload() ---


def test_parse_payload_valid(strategy):
    """Vérifie l'extraction de la liste des stations depuis un payload GBFS standard."""
    raw_data = {
        "data": {
            "stations": [
                {
                    "station_id": "st_001",
                    "name": "Station 1",
                    "lat": 48.8,
                    "lon": 2.3,
                    "capacity": 20,
                },
                {
                    "station_id": "st_002",
                    "name": "Station 2",
                    "lat": 48.9,
                    "lon": 2.4,
                    "capacity": 15,
                },
            ]
        }
    }

    stations = strategy.parse_payload(raw_data)

    assert len(stations) == 2
    assert stations[0].station_id == "st_001"
    assert stations[1].station_id == "st_002"


def test_parse_payload_empty_or_malformed(strategy):
    """Vérifie la robustesse face à des données vides ou mal formées."""
    assert strategy.parse_payload({}) == []
    assert strategy.parse_payload(None) == []
    assert strategy.parse_payload({"data": {}}) == []
    assert strategy.parse_payload({"data": {"stations": []}}) == []
    assert strategy.parse_payload({"other_key": 123}) == []


# --- Tests de persist() ---


@pytest.mark.anyio
async def test_persist_ok(strategy, mock_dao):
    """Vérifie la persistance par lots via le DAO et le décompte des succès."""
    st1 = StationInformation(station_id="1", name="S1", lat=48.0, lon=2.0, capacity=10)
    st2 = StationInformation(station_id="2", name="S2", lat=48.1, lon=2.1, capacity=10)

    mock_dao.upsert_station_info.side_effect = [True, False]

    count = await strategy.persist([st1, st2])

    assert count == 1
    assert mock_dao.upsert_station_info.call_count == 2


@pytest.mark.anyio
async def test_persist_empty(strategy, mock_dao):
    """Vérifie que la persistance d'une liste vide renvoie 0 sans appel au DAO."""
    count = await strategy.persist([])
    assert count == 0
    mock_dao.upsert_station_info.assert_not_called()


# --- Test bout en bout de execute() ---


@pytest.mark.anyio
async def test_execute_e2e(strategy, mock_dao, mock_http_client):
    """Vérifie l'exécution complète depuis le téléchargement HTTP jusqu'à la persistance."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {
        "data": {
            "stations": [
                {
                    "station_id": "st_e2e",
                    "name": "Station E2E",
                    "lat": 48.8,
                    "lon": 2.3,
                    "capacity": 25,
                }
            ]
        }
    }
    mock_http_client.get.return_value = mock_response
    mock_dao.upsert_station_info.return_value = True

    await strategy.execute()

    mock_http_client.get.assert_called_once_with(
        "https://api.test/station_information.json"
    )
    assert mock_dao.upsert_station_info.call_count == 1

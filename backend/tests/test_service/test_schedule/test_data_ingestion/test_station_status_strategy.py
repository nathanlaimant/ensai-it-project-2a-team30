from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from business_object.station_state import StationState
from business_object.station_status import StationStatus
from dao.station_status_dao import StationStatusDAO
from service.schedule.data_ingestion.station_status_strategy import (
    StationStatusStrategy,
)


@pytest.fixture
def mock_dao():
    return MagicMock(spec=StationStatusDAO)


@pytest.fixture
def mock_http_client():
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def strategy(mock_dao, mock_http_client):
    return StationStatusStrategy(
        dao=mock_dao,
        feed_name="station_status",
        url="https://api.test/station_status.json",
        http_client=mock_http_client,
    )


# --- Tests de _classify_vehicle_type() ---


@pytest.mark.parametrize(
    "raw_name,expected_category",
    [
        (None, "mechanical"),
        ("", "mechanical"),
        ("mechanical", "mechanical"),
        ("mécanique", "mechanical"),
        ("vélo classique", "mechanical"),
        ("non-electric", "mechanical"),
        ("nonelectric", "mechanical"),
        ("sans assistance", "mechanical"),
        ("pas elec", "mechanical"),
        ("unassisted", "mechanical"),
        ("electric", "electric"),
        ("électrique", "electric"),
        ("electrique", "electric"),
        ("e-bike", "electric"),
        ("ebike", "electric"),
        ("e_bike", "electric"),
        ("pedelec", "electric"),
        ("epedelec", "electric"),
        ("VAE", "electric"),
        ("booster", "electric"),
        ("trottinette", "electric"),
        ("scooter", "electric"),
        ("battery powered", "electric"),
        ("motorized", "electric"),
        ("power assist", "electric"),
        ("voi-scooter", "electric"),
        ("tier-bike", "electric"),
        ("dott-scooter", "electric"),
        ("lime-s", "electric"),
    ],
)
def test_classify_vehicle_type(raw_name, expected_category):
    """Vérifie la catégorisation robuste des types de véhicules."""
    assert StationStatusStrategy._classify_vehicle_type(raw_name) == expected_category


# --- Tests de _parse_vehicle_types() ---


def test_parse_vehicle_types_empty():
    """Retourne la valeur par défaut en cas de données vides."""
    res = StationStatusStrategy._parse_vehicle_types(None, default=5)
    assert res == {"mechanical": 5, "electric": 0}


def test_parse_vehicle_types_standard_gbfs():
    """Format standard GBFS : liste de dictionnaires avec vehicle_type_id et count."""
    raw_data = [
        {"vehicle_type_id": "mechanical", "count": 8},
        {"vehicleTypeId": "e-bike", "count": "4"},
        {"vehicle_type": "invalid_count", "count": "bad_int"},
        "not_a_dict_skipped",
    ]
    res = StationStatusStrategy._parse_vehicle_types(raw_data)
    assert res == {"mechanical": 8, "electric": 4}


def test_parse_vehicle_types_velib_format():
    """Format alternatif Vélib : liste de dictionnaires type: count."""
    raw_data = [
        {"mechanical": 7},
        {"electric": 3},
        {"invalid": "non_integer"},
    ]
    res = StationStatusStrategy._parse_vehicle_types(raw_data)
    assert res == {"mechanical": 7, "electric": 3}


def test_parse_vehicle_types_dict_format():
    """Format dictionnaire direct : type: count."""
    raw_data = {"mecanique": 6, "electrique": "5", "bad": "invalid_int"}
    res = StationStatusStrategy._parse_vehicle_types(raw_data)
    assert res == {"mechanical": 6, "electric": 5}


# --- Tests de _parse_vehicle_docks() ---


def test_parse_vehicle_docks():
    """Vérifie l'analyse des bornes disponibles par type."""
    # Données vides
    assert StationStatusStrategy._parse_vehicle_docks(None, default=10) == {
        "mechanical": 10,
        "electric": 10,
    }

    # Liste format GBFS standard avec vehicle_type_ids et gestion des entiers invalides
    raw_standard = [
        {"vehicle_type_ids": ["mechanical"], "count": 12},
        {"vehicleTypeIds": ["electric", "vae"], "count": "8"},
        {"vehicle_type_ids": ["mechanical"], "count": "bad_int"},
        "skip_non_dict",
    ]
    res_std = StationStatusStrategy._parse_vehicle_docks(raw_standard)
    assert res_std["mechanical"] == 12
    assert res_std["electric"] == 8

    # Liste format Vélib
    raw_velib = [
        {"mechanical": 5},
        {"electric": "15"},
        {"mechanical": "bad_val"},
    ]
    res_velib = StationStatusStrategy._parse_vehicle_docks(raw_velib)
    assert res_velib["mechanical"] == 5
    assert res_velib["electric"] == 15

    # Format dictionnaire
    raw_dict = {"mechanical": 4, "electric": 6, "other": "bad_int"}
    assert StationStatusStrategy._parse_vehicle_docks(raw_dict) == {
        "mechanical": 4,
        "electric": 6,
    }


# --- Tests de from_json_dict() & classification d'état ---


def test_from_json_dict_functional(strategy):
    """Station normale opérationnelle."""
    payload = {
        "station_id": "st_101",
        "num_bikes_available": 10,
        "num_docks_available": 15,
        "num_bikes_disabled": 1,
        "num_docks_disabled": 0,
        "is_installed": True,
        "is_renting": True,
        "is_returning": True,
        "last_reported": 1704110400,  # 2024-01-01 12:00:00 UTC
        "vehicle_types_available": [
            {"vehicle_type_id": "mechanical", "count": 6},
            {"vehicle_type_id": "electric", "count": 4},
        ],
    }

    st = strategy.from_json_dict(payload)

    assert isinstance(st, StationStatus)
    assert st.station_id == "st_101"
    assert st.num_bikes_available == 10
    assert st.num_docks_available == 15
    assert st.operational_capacity == 25
    assert st.station_state == StationState.FUNCTIONAL
    assert st.vehicle_types_available == {"mechanical": 6, "electric": 4}
    assert isinstance(st.last_reported, datetime)


def test_from_json_dict_recomputes_bikes_from_vehicle_types(strategy):
    """Recompte le nombre de vélos à partir des types si num_bikes_available est 0 ou None."""
    payload = {
        "station_id": "st_102",
        "numBikesAvailable": 0,
        "numDocksAvailable": 10,
        "numBikesDisabled": 0,
        "numDocksDisabled": 0,
        "last_reported": 1704110400,
        "vehicle_types_available": [
            {"vehicle_type_id": "mechanical", "count": 5},
            {"vehicle_type_id": "electric", "count": 5},
        ],
    }

    st = strategy.from_json_dict(payload)

    assert st.num_bikes_available == 10
    assert st.operational_capacity == 20


@pytest.mark.parametrize(
    "override_fields,expected_state",
    [
        ({"is_installed": False}, StationState.EMPTY),
        ({"num_bikes_available": 0, "vehicle_types_available": []}, StationState.EMPTY),
        ({"is_renting": False}, StationState.EMPTY),
        ({"num_docks_available": 0}, StationState.FULL),
        ({"is_returning": False}, StationState.FULL),
    ],
)
def test_from_json_dict_station_state_classification(
    strategy, override_fields, expected_state
):
    """Vérifie les critères de classification en EMPTY et FULL."""
    base_payload = {
        "station_id": "st_test",
        "num_bikes_available": 5,
        "num_docks_available": 5,
        "is_installed": True,
        "is_renting": True,
        "is_returning": True,
        "last_reported": 1704110400,
    }
    base_payload.update(override_fields)

    st = strategy.from_json_dict(base_payload)

    assert st.station_state == expected_state


# --- Tests de parse_payload() ---


def test_parse_payload(strategy):
    """Vérifie l'analyse de payload GBFS valide et la gestion des données vides."""
    raw = {
        "data": {
            "stations": [
                {
                    "station_id": "s1",
                    "num_bikes_available": 5,
                    "num_docks_available": 5,
                    "last_reported": 1704110400,
                }
            ]
        }
    }
    res = strategy.parse_payload(raw)
    assert len(res) == 1
    assert res[0].station_id == "s1"

    assert strategy.parse_payload({}) == []
    assert strategy.parse_payload(None) == []


# --- Tests de persist() ---


@pytest.mark.anyio
async def test_persist(strategy, mock_dao):
    """Vérifie la délégation au bulk_insert_status du DAO."""
    status = StationStatus(
        station_id="s1",
        num_bikes_available=5,
        num_bikes_disabled=0,
        num_docks_available=5,
        num_docks_disabled=0,
        operational_capacity=10,
        last_reported=datetime.now(UTC),
        vehicle_types_available=None,
        vehicle_docks_available=None,
        station_state=StationState.FUNCTIONAL,
    )

    mock_dao.bulk_insert_status.return_value = 1

    count = await strategy.persist([status])

    assert count == 1
    mock_dao.bulk_insert_status.assert_called_once_with([status])

    # Cas vide
    assert await strategy.persist([]) == 0


# --- Test execute() e2e ---


@pytest.mark.anyio
async def test_execute_e2e(strategy, mock_dao, mock_http_client):
    """Vérifie le cycle complet de execute()."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {
        "data": {
            "stations": [
                {
                    "station_id": "st_status_e2e",
                    "num_bikes_available": 10,
                    "num_docks_available": 10,
                    "last_reported": 1704110400,
                }
            ]
        }
    }
    mock_http_client.get.return_value = mock_response
    mock_dao.bulk_insert_status.return_value = 1

    await strategy.execute()

    assert mock_dao.bulk_insert_status.call_count == 1

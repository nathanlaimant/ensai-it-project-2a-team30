from datetime import date
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from business_object.system_information import SystemInformation
from dao.system_information_dao import SystemInformationDAO
from service.schedule.data_ingestion.system_information_strategy import (
    SystemInformationStrategy,
)


@pytest.fixture
def mock_dao():
    return MagicMock(spec=SystemInformationDAO)


@pytest.fixture
def mock_http_client():
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def strategy(mock_dao, mock_http_client):
    return SystemInformationStrategy(
        dao=mock_dao,
        feed_name="system_information",
        url="https://api.test/system_information.json",
        http_client=mock_http_client,
    )


# --- Tests de from_json_dict() ---


def test_from_json_dict_full(strategy):
    """Vérifie la conversion complète d'un dictionnaire JSON en SystemInformation."""
    payload = {
        "system_id": "veloscope_paris",
        "language": "fr",
        "name": "VéloScope Paris",
        "url": "https://veloscope.fr",
        "start_date": "2020-01-15",
        "phone_number": "0123456789",
        "email": "contact@veloscope.fr",
        "timezone": "Europe/Paris",
    }

    sys_info = strategy.from_json_dict(payload)

    assert isinstance(sys_info, SystemInformation)
    assert sys_info.system_id == "veloscope_paris"
    assert sys_info.language == "fr"
    assert sys_info.name == "VéloScope Paris"
    assert sys_info.url == "https://veloscope.fr"
    assert sys_info.start_date == date(2020, 1, 15)
    assert sys_info.phone_number == "0123456789"
    assert sys_info.email == "contact@veloscope.fr"
    assert sys_info.timezone == "Europe/Paris"


def test_from_json_dict_minimal(strategy):
    """Vérifie la conversion lorsque les champs optionnels sont None ou absents."""
    payload = {
        "system_id": "sys_min",
        "language": "en",
        "name": "Minimal System",
        "timezone": "UTC",
    }

    sys_info = strategy.from_json_dict(payload)

    assert sys_info.system_id == "sys_min"
    assert sys_info.language == "en"
    assert sys_info.name == "Minimal System"
    assert sys_info.timezone == "UTC"
    assert sys_info.url is None
    assert sys_info.start_date is None
    assert sys_info.phone_number is None
    assert sys_info.email is None


# --- Tests de parse_payload() ---


def test_parse_payload_valid(strategy):
    """Vérifie l'analyse d'un payload standard GBFS system_information."""
    raw_data = {
        "data": {
            "system_id": "sys_1",
            "language": "fr",
            "name": "System 1",
            "timezone": "Europe/Paris",
        }
    }

    res = strategy.parse_payload(raw_data)

    assert len(res) == 1
    assert res[0].system_id == "sys_1"
    assert res[0].name == "System 1"


def test_parse_payload_empty_and_malformed(strategy):
    """Vérifie le retour [] en cas de payload vide ou mal formé."""
    assert strategy.parse_payload({}) == []
    assert strategy.parse_payload(None) == []
    assert strategy.parse_payload({"data": {}}) == []


# --- Tests de persist() ---


@pytest.mark.anyio
async def test_persist(strategy, mock_dao):
    """Vérifie la délégation à upsert_system_info et le comptage des succès."""
    s1 = SystemInformation(
        system_id="s1",
        language="fr",
        name="Sys 1",
        timezone="UTC",
        url=None,
        start_date=None,
        phone_number=None,
        email=None,
    )
    s2 = SystemInformation(
        system_id="s2",
        language="en",
        name="Sys 2",
        timezone="UTC",
        url=None,
        start_date=None,
        phone_number=None,
        email=None,
    )

    mock_dao.upsert_system_info.side_effect = [True, False]

    count = await strategy.persist([s1, s2])

    assert count == 1
    assert mock_dao.upsert_system_info.call_count == 2

    # Cas vide
    assert await strategy.persist([]) == 0


# --- Test execute() e2e ---


@pytest.mark.anyio
async def test_execute_e2e(strategy, mock_dao, mock_http_client):
    """Vérifie le cycle complet de execute()."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {
        "data": {
            "system_id": "sys_e2e",
            "language": "fr",
            "name": "System E2E",
            "timezone": "Europe/Paris",
        }
    }
    mock_http_client.get.return_value = mock_response
    mock_dao.upsert_system_info.return_value = True

    await strategy.execute()

    mock_http_client.get.assert_called_once_with("https://api.test/system_information.json")
    assert mock_dao.upsert_system_info.call_count == 1

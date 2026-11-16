from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from service.schedule.data_ingestion.feed_ingestion_strategy import BaseIngestionStrategy


class DummyIngestionStrategy(BaseIngestionStrategy[dict]):
    """Sous-classe concrète pour tester la logique de BaseIngestionStrategy."""

    def parse_payload(self, raw_data: Any) -> list[dict]:
        if not raw_data:
            return []
        return raw_data.get("items", [])

    async def persist(self, records: list[dict]) -> int:
        return len(records)


class IncompleteIngestionStrategy(BaseIngestionStrategy[dict]):
    """Sous-classe n'implémentant pas les méthodes abstraites pour tester NotImplementedError."""

    def parse_payload(self, raw_data: Any) -> list[dict]:
        return super().parse_payload(raw_data)

    async def persist(self, records: list[dict]) -> int:
        return await super().persist(records)


@pytest.fixture
def mock_http_client():
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def dummy_strategy(mock_http_client):
    return DummyIngestionStrategy(
        feed_name="dummy_feed",
        url="https://api.test/feed.json",
        http_client=mock_http_client,
    )


# --- Tests de fetch_feed() ---


@pytest.mark.anyio
async def test_fetch_feed_ok(dummy_strategy, mock_http_client):
    """Vérifie la récupération et la désérialisation JSON du flux."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"items": [{"id": 1}, {"id": 2}]}
    mock_http_client.get.return_value = mock_response

    data = await dummy_strategy.fetch_feed()

    assert data == {"items": [{"id": 1}, {"id": 2}]}
    mock_http_client.get.assert_called_once_with("https://api.test/feed.json")
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.anyio
async def test_fetch_feed_http_error(dummy_strategy, mock_http_client):
    """Vérifie la propagation des erreurs HTTP lors de fetch_feed."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", request=MagicMock(), response=mock_response
    )
    mock_http_client.get.return_value = mock_response

    with pytest.raises(httpx.HTTPStatusError):
        await dummy_strategy.fetch_feed()


# --- Tests des méthodes abstraites ---


@pytest.mark.anyio
async def test_abstract_methods_raise_not_implemented(mock_http_client):
    """Vérifie que les méthodes abstraites de base lèvent NotImplementedError."""
    incomplete = IncompleteIngestionStrategy(
        feed_name="incomplete",
        url="https://api.test/feed.json",
        http_client=mock_http_client,
    )

    with pytest.raises(NotImplementedError):
        incomplete.parse_payload({})

    with pytest.raises(NotImplementedError):
        await incomplete.persist([])


# --- Tests de execute() ---


@pytest.mark.anyio
async def test_execute_success(dummy_strategy, mock_http_client):
    """Vérifie le déroulement complet de execute() : fetch -> parse -> persist."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"items": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}
    mock_http_client.get.return_value = mock_response

    await dummy_strategy.execute()

    mock_http_client.get.assert_called_once_with("https://api.test/feed.json")


@pytest.mark.anyio
async def test_execute_catches_exception_safely(dummy_strategy, mock_http_client):
    """Vérifie que execute() intercepte les exceptions réseau sans faire planter le scheduler."""
    mock_http_client.get.side_effect = httpx.ConnectError("Connexion refusée")

    # Ne doit pas lever d'exception
    await dummy_strategy.execute()

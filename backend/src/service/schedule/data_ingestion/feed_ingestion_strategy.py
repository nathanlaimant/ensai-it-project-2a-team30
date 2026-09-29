from abc import ABC, abstractmethod
from typing import Any

import httpx


class FeedIngestionStrategy[T](ABC):
    """Define the contract for a feed ingestion strategy."""

    def __init__(
        self,
        feed_name: str,
        url: str,
        interval_seconds: int,
        http_client: httpx.AsyncClient,
    ):
        self.feed_name = feed_name
        self.url = url
        self.interval_seconds = interval_seconds
        self.http_client = http_client

    async def fetch_feed(self) -> Any:
        """Fetch JSON payload."""
        response = await self.http_client.get(self.url)
        return response.json()

    @abstractmethod
    def parse_payload(self, raw_data: Any) -> list[T]:
        """Parse a feed payload into domain records."""
        raise NotImplementedError

    @abstractmethod
    async def persist(self, records: list[T]) -> int:
        """Persist parsed domain records."""
        raise NotImplementedError

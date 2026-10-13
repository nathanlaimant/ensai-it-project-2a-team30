from abc import ABC, abstractmethod
from typing import Any

import httpx

from utils.log_utils import get_logger

logger = get_logger(__name__)


class BaseIngestionStrategy[T](ABC):
    """Define the contract for a feed ingestion strategy."""

    def __init__(
        self,
        feed_name: str,
        url: str,
        http_client: httpx.AsyncClient,
    ):
        self.feed_name = feed_name
        self.url = url
        self.http_client = http_client

    async def fetch_feed(self) -> Any:
        """Fetch JSON payload."""
        response = await self.http_client.get(self.url)
        response.raise_for_status()
        return response.json()

    @abstractmethod
    def parse_payload(self, raw_data: Any) -> list[T]:
        """Parse a feed payload into domain records."""
        raise NotImplementedError

    @abstractmethod
    async def persist(self, records: list[T]) -> int:
        """Persist parsed domain records."""
        raise NotImplementedError

    async def execute(self) -> None:
        """Execute the ingestion strategy."""
        try:
            raw_data = await self.fetch_feed()
            records = self.parse_payload(raw_data)
            count = await self.persist(records)
            logger.info(f"{self.feed_name}: {count} records ingested.")
        except Exception as e:
            logger.error(f"Error during {self.feed_name} ingestion: {e}")

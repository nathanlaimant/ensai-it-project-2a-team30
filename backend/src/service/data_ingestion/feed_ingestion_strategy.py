from abc import ABC, abstractmethod
from typing import Generic, TypeVar


Record = TypeVar("Record")


class FeedIngestionStrategy(ABC, Generic[Record]):
    """Define the contract for a feed ingestion strategy."""

    def __init__(self, feed_name: str, interval_seconds: int, url: str):
        self.feed_name = feed_name
        self.interval_seconds = interval_seconds
        self.url = url

    @abstractmethod
    def parse_payload(self, headers: dict, raw_data: dict) -> list[Record]:
        """Parse a feed payload into domain records."""
        raise NotImplementedError

    @abstractmethod
    def persist(self, records: list[Record]) -> int:
        """Persist parsed domain records."""
        raise NotImplementedError
